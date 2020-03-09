from abc import ABC, abstractmethod, abstractstaticmethod
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Page import Page
from mediastrends.stats.Stats import Stats


class DbManager(ABC):

    def __init__(self, config):
        self.cfg = config

    @abstractstaticmethod
    def db_to_torrent(db_torrent):
        return

    @abstractstaticmethod
    def db_to_tracker(db_tracker):
        return

    @abstractstaticmethod
    def db_to_page(db_page):
        return

    @abstractstaticmethod
    def tracker_to_db(tracker: Tracker):
        return

    @abstractstaticmethod
    def torrent_to_db(torrent: Torrent):
        return

    @abstractstaticmethod
    def save_page(page: Page, torrent: Torrent, tracker: Tracker):
        return

    @abstractstaticmethod
    def save_torrent_tracker(torrent: Torrent, tracker: Tracker):
        return

    @abstractstaticmethod
    def save_stats(stats: Stats, torrent: Torrent, tracker: Tracker):
        return

    @abstractstaticmethod
    def get_torrent_by_hash(hash_info: str):
        return

    @abstractstaticmethod
    def get_tracker_by_name(name: str):
        return