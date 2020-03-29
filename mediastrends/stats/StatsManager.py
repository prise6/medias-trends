import datetime
from mediastrends import logger_app
from mediastrends.database.DbManager import DbManager
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Torrent import Torrent
from mediastrends.trends.TrendsManager import TrendsManager
from mediastrends.trends.TrendsEngine import ClassicTrendsEngine
from .StatsCollection import StatsCollection

class StatsManager():

    def __init__(self, config, dbmanager: DbManager):
        self.cfg = config
        self._dbmanager = dbmanager
        self._trends_manager = TrendsManager(config, dbmanager)
        self._torrents_new = []
        self._torrents_follow = []
        self._torrents_unfollow = []

    @property
    def torrents_new(self):
        if not self._torrents_new:
            try:
                self._torrents_new = self._dbmanager.get_torrents_by_status(1)
            except ValueError as err:
                logger_app.info("new torrents is empty")
        return self._torrents_new

    @property
    def torrents_follow(self):
        if not self._torrents_follow:
            try:
                self._torrents_follow = self._dbmanager.get_torrents_by_status(2)
            except ValueError as err:
                logger_app.info("torrent to follow is empty")
        return self._torrents_follow

    @property
    def torrents_unfollow(self):
        if not self._torrents_unfollow:
            try:
                self._torrents_unfollow = self._dbmanager.get_torrents_by_status(0)
            except ValueError as err:
                logger_app.info("torrent to unfollow is empty")

        return self._torrents_unfollow

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

    def compute_torrents_status(self):
        """
        From new and follow torrents, compute which are not welcome anymore
        """
        today = datetime.datetime.today()
        torrents_new = []
        torrents_unfollow = []
        torrents_follow = []
        staging = []

        ## new -> follow | unfollow
        candidates = self.torrents_new
        for t in candidates:
            if (today-t.pub_date).days < self.cfg.getint('stats_manager', 'new_delay'):
                torrents_new.append(t)
                continue
            staging.append(t)
        
        ## follow -> unfollow
        ### (factoriser un jour)
        candidates = self.torrents_follow + staging
        candidates_stats = [self.get_stats_collection(t) for t in candidates]
        self._trends_manager.evaluate(candidates_stats, ClassicTrendsEngine())
        for sc in self._trends_manager.is_trending:
            for s in sc.stats:
                s.torrent.follow()
                torrents_follow.append(s.torrent)
        for sc in self._trends_manager.is_not_trending:
            for s in sc.stats:
                s.torrent.unfollow()
                torrents_unfollow.append(s.torrent)

        self._torrents_new = torrents_new
        self._torrents_follow = torrents_follow
        self._torrents_unfollow = torrents_unfollow

        logger_app.info("Updated torrents status: new (%s), follow (%s), unfollow (%s)" % (
            len(torrents_new),
            len(torrents_follow),
            len(torrents_unfollow)
        ))
                
        return self

    def update_torrents_status(self):
        """
        only torrents follow and unfollow has to be updated
        """
        self.compute_torrents_status()
        nb_rows_updated = 0
        for torrent in self._torrents_follow + self._torrents_unfollow:
            _, c = self._dbmanager.update(torrent)
            nb_rows_updated += c

        return nb_rows_updated

    def get_torrents_by_tracker(self, tracker: Tracker, status = [1, 2], category = [0, 1, 2]):
        """
        Return torrents list according to tracker to get stats from
        """

        return self._dbmanager.get_torrents_by_tracker(tracker, status = status, category = category)




        

