import datetime
from .Tracker import Tracker


class Torrent:
    
    def __init__(self, hash_info: str, title: str, add_date: datetime.date, tracker: Tracker):
        self._hash_info = hash_info
        self._title = title
        self._add_date = add_date
        self._tracker = tracker

    @property
    def hash_info(self):
        return self._hash_info

    @property
    def title(self):
        return self._title

    @property
    def add_date(self):
        return self._add_date

    @property
    def tracker(self):
        return self._tracker