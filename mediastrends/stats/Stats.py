import datetime
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Page import Page


class Stats():

    def __init__(self, torrent: Torrent, tracker: Tracker, valid_date: datetime.datetime, leechers: int = None, seeders: int = None, completed: int = None):
        self._leechers = leechers
        self._seeders = seeders
        self._completed = completed
        self._valid_date = valid_date
        self._tracker = tracker
        self._torrent = torrent

    @property
    def leechers(self):
        return self._leechers

    @leechers.setter
    def leechers(self, leechers: int):
        self._leechers = leechers
        return self

    @property
    def seeders(self):
        return self._seeders

    @seeders.setter
    def seeders(self, seeders: int):
        self._seeders = seeders
        return self

    @property
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, completed: int):
        self._completed = completed
        return self

    @property
    def valid_date(self):
        return self._valid_date

    @valid_date.setter
    def valid_date(self, valid_date: datetime.datetime):
        self._valid_date = valid_date
        return self

    @property
    def torrent(self):
        return self._torrent

    @torrent.setter
    def torrent(self, torrent: Torrent):
        self._torrent = torrent
        return self

    @property
    def tracker(self):
        return self._tracker

    @tracker.setter
    def tracker(self, tracker: Tracker):
        self._tracker = tracker
        return self


#
# use python way to create "classmethod"
#

def stats_from_page(page: Page, torrent: Torrent, tracker: Tracker):
    return Stats(
        torrent = torrent,
        tracker = tracker,
        leechers = page.leechers,
        seeders = page.seeders,
        completed = page.completed,
        valid_date = page.scrape_date
    )
