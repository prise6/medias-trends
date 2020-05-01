import logging
import dateutil.parser
import xml.etree.ElementTree as ET
from mediastrends.torrent.Torrent import Torrent, TorrentFile

logger = logging.getLogger(__name__)


_TORZNAB_RESULTS_FIELDS = {
    "title": str,
    "guid": str,
    "jackettindexer": str,
    "comments": str,
    "pubDate": lambda d: dateutil.parser.parse(d, ignoretz=True),
    "size": int,
    "files": int,
    "grabs": int,
    "description": str,
    "link": str,
    "category": int,
    "magneturl": str,
    "rageid": int,
    "thetvdb": int,
    "imdb": str,
    "seeders": int,
    "peers": int,
    "infohash": lambda ih: str(ih).lower(),
    "minimumratio": float,
    "minimumseedtime": int,
    "downloadvolumefactor": float,
    "uploadvolumefactor": float,
}


_JACKETT_CATEGORIES = {
    Torrent._CAT_MOVIE: [2000, 3000],
    Torrent._CAT_SERIE: [5000, 6000]
}


class TorznabJackettRSS():

    def __init__(self, feed: str):
        self._feed = feed
        self.items = []
        self._feed_parsed = None

    def parse(self):
        self._feed_parsed = ET.fromstring(self._feed)

        if 'error' == self._feed_parsed.tag:
            raise Exception(self._feed_parsed.get('description'))

    @staticmethod
    def get_value(item, key):
        for child in item:
            if child.tag == key:
                return child.text
            if child.attrib and child.attrib.get('name'):
                if child.attrib.get('name') == key:
                    return child.attrib.get('value')
        return None

    def process_items(self):
        self.parse()

        for item in self._feed_parsed.findall('./channel/item'):
            fields_values = {field: formatter(TorznabJackettRSS.get_value(item, field)) for field, formatter in _TORZNAB_RESULTS_FIELDS.items() if TorznabJackettRSS.get_value(item, field) is not None}
            self.items.append(TorznabJackettResult(fields_values))

        if not self.items:
            logger.warning('List items is empty')

        return self


class TorznabJackettResult():

    def __init__(self, dict_: dict = None):

        self._elements = dict.fromkeys(_TORZNAB_RESULTS_FIELDS.keys(), None)
        self._elements.update(dict_)

    def get(self, key, default=None):
        return self._elements.get(key, default)

    def update(self, key, value):
        self._elements.update({key: value})
        return self

    @staticmethod
    def transform_category(jackett_category):
        for app_cat, bounds in _JACKETT_CATEGORIES.items():
            if jackett_category >= bounds[0] and jackett_category < bounds[1]:
                return app_cat
        return Torrent._CAT_UNKNOWN

    def to_torrent_file(self):

        torrent_file = TorrentFile(
            resource=self.get('link'),
            info_hash=self.get('infohash'),
            name=self.get('title'),
            pub_date=self.get('pubDate'),
            size=self.get('size'),
            category=TorznabJackettResult.transform_category(self.get('category'))
        )
        if self.get('imdb', None):
            logger.debug("Imdb_id is already known")
            torrent_file.imdb_id = self.get('imdb', None)

        return torrent_file
