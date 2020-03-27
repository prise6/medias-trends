import numpy as np
from mediastrends import logger_app
from mediastrends.database.DbManager import DbManager
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Torrent import Torrent
from mediastrends.stats import StatsCollection
from mediastrends.trends.TrendsEngine import TrendsEngine

class TrendsManager():

    def __init__(self, config, dbmanager: DbManager):
        self.cfg = config
        self._dbmanager = dbmanager
        self._is_trending = []
        self._is_not_trending = []

    @property
    def is_trending(self):
        return self._is_trending

    @property
    def is_not_trending(self):
        return self._is_not_trending

    def evaluate(self, stats_collections: list, trend_engine: TrendsEngine = None):

        nb_to_keep = int(np.ceil(self.cfg.getfloat('trends', 'tau') * len(stats_collections)))
        
        scores = np.array([trend_engine.score(s) for s in stats_collections])
        item_sorted = np.argsort(scores)[::-1]

        self._is_trending = [stats_collections[index] for index in item_sorted[:nb_to_keep]]
        self._is_not_trending = [stats_collections[index] for index in item_sorted[nb_to_keep:]]

        return self
