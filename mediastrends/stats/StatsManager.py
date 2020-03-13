from mediastrends.database.peewee.PDbManager import PDbManager


class StatsManager():

    def __init__(self, config):
        self.cfg = config
        self._torrents_new = []
        self._torrents_follow = []
        self._torrents_to_unfollow = []

    @property
    def torrents_new(self):
        if not self._torrents_new:
            self._torrents_new = PDbManager.get_torrents_by_status(1)
        return self._torrents_new

    @property
    def torrents_follow(self):
        if not self._torrents_follow:
            self._torrents_follow = PDbManager.get_torrents_by_status(2)
        return self._torrents_follow

    @torrents_new.setter
    def torrents_new(self, torrents_new: list):
        self._torrents_new = torrents_new
        return self

    @torrents_follow.setter
    def torrents_follow(self, torrents_follow: list):
        self._torrents_follow = torrents_follow
        return self

    @torrents_unfollow.setter
    def torrents_unfollow(self, torrents_unfollow: list):
        self._torrents_unfollow = torrents_unfollow
        return self


    