import logging
from retry import retry
import requests

from mediastrends import config
import mediastrends.tools as tools
from mediastrends.torrent.Tracker import Tracker, HttpTracker, UdpTracker
from mediastrends.stats.Stats import Stats
from mediastrends.stats.StatsCollection import StatsCollection

logger = logging.getLogger(__name__)


class StatsScraper():

    _HEADERS = {}
    _HEADERS['user-agent'] = config.get('requests', 'user_agent')
    _BATCH_SIZE = config.getint('requests', 'batch_size')
    _RETRIES = config.getint('retry', 'tries')
    _DELAY = config.getint('retry', 'delay')

    def __init__(self, tracker: Tracker):
        self.tracker = tracker
        self._torrents_lookup = {}
        self._info_hashes = []
        self._parsed_content = {}

    @property
    def tracker(self):
        return self._tracker

    @tracker.setter
    def tracker(self, tracker: Tracker):
        if not (isinstance(tracker, HttpTracker) or isinstance(tracker, UdpTracker)):
            raise TypeError('Tracker object must be instance of HttpTracker or UdpTracker')
        self._tracker = tracker

    @property
    def torrents(self):
        return self._torrents

    @torrents.setter
    def torrents(self, torrents: list):
        self._torrents_lookup = {t.info_hash: t for t in torrents}
        self._parsed_content = {}

    @property
    def stats_collection(self):
        return StatsCollection([Stats(
            torrent=self._torrents_lookup[info_hash],
            tracker=self._tracker,
            seeders=c.get('complete'),
            leechers=c.get('incomplete'),
            completed=c.get('downloaded')
        ) for info_hash, c in self._parsed_content.items()])

    @retry((requests.exceptions.RequestException, OSError), tries=_RETRIES, delay=_DELAY, jitter=(3, 10), logger=logger)
    def run(self, info_hashes: list):
        content_infos = self._tracker.scrape(info_hashes)
        self._parsed_content.update(content_infos)

    def run_by_batch(self):
        full_infos_hashes_list = list(self._torrents_lookup.keys())
        logger.debug("Run by batch of %s" % self._BATCH_SIZE)
        for info_hashes in tools.batch(full_infos_hashes_list, self._BATCH_SIZE):
            try:
                self.run(info_hashes)
            except (requests.exceptions.RequestException, OSError) as err:
                logger.warning(err)
                continue
