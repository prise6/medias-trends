import datetime
from .Tracker import Tracker


class Torrent:
    
    def __init__(self, hash_info: str, name: str, pub_date: datetime.date, tracker: Tracker):
        self._hash_info = hash_info
        self._name = name
        self._pub_date = pub_date
        self._tracker = tracker

    @property
    def hash_info(self):
        return self._hash_info

    @property
    def name(self):
        return self._name

    @property
    def pub_date(self):
        return self._pub_date

    @property
    def tracker(self):
        return self._tracker