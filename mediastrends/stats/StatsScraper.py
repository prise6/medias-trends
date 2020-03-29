import urllib.parse
import random
import datetime
import time
from retry import retry
import requests

from mediastrends import logger_app, config
import mediastrends.tools as tools
from mediastrends.torrent.Tracker import Tracker
from mediastrends.stats.Stats import Stats
from mediastrends.stats.StatsCollection import StatsCollection


class StatsScraper():

    _HEADERS = {}
    _HEADERS['user-agent'] = config.get('requests', 'user_agent')
    _BATCH_SIZE = config.getint('requests', 'batch_size')
    _RETRIES = config.getint('retry', 'tries')
    _DELAY = config.getint('retry', 'delay')
    
    def __init__(self, tracker: Tracker):
        self._tracker = tracker
        self._torrents_lookup = {}
        self._info_hashes = []
        self._parsed_content = {}

    @property
    def tracker(self):
        return self._tracker

    @tracker.setter
    def tracker(self, tracker: Tracker):
        self._tracker = tracker

    @property
    def torrents(self):
        return self._torrents

    @torrents.setter
    def torrents(self, torrents: list):
        self._torrents_lookup = { t.info_hash: t for t in torrents }
        self._info_hashes = self.extract_info_hashes()
        self._parsed_content = {}

    @property
    def stats_collection(self):
        return StatsCollection([Stats(
            torrent = self._torrents_lookup[info_hash],
            tracker = self._tracker,
            seeders = c.get('complete'),
            leechers = c.get('incomplete'),
            completed = c.get('downloaded')
        ) for info_hash, c in self._parsed_content.items()])
    
    def extract_info_hashes(self):
        return [('info_hash', bytes.fromhex(info_hash)) for info_hash in self._torrents_lookup.keys()]

    def url(self, info_hashes: list):
        url_split = urllib.parse.urlsplit(self._tracker.url)
        url_split = list(url_split)
        url_split[3] = urllib.parse.urlencode(info_hashes)
        url = urllib.parse.urlunsplit(url_split)

        return url

    @retry(requests.exceptions.RequestException, tries=_RETRIES, delay=_DELAY, jitter=(3, 10))
    def run(self, info_hashes: list):
        logger_app.info('---> Building scrape url ...')
        url = self.url(info_hashes)
        logger_app.info('---> Contacting Tracker ...')
        content = tools.get_request_content(url, self._HEADERS)
        logger_app.info('---> Parse content ...')
        self._parsed_content.update(tools.parse_bencode_tracker('scrape', content))
        logger_app.info('---> Done.')


    def run_by_batch(self):
        for info_hashes in tools.batch(self._info_hashes, self._BATCH_SIZE):
            try:
                self.run(info_hashes)
            except requests.exceptions.RequestException as err:
                logger_app.warning(err)
                continue
    


