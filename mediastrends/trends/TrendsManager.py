import numpy as np
import datetime
from mediastrends import logger_app
from mediastrends.database.DbManager import DbManager
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Torrent import Torrent
from mediastrends.stats import StatsCollection
from mediastrends.trends.TrendsEngine import TrendsEngine

class TrendsManager():

    def __init__(self, config, dbmanager: DbManager, category: list = None, mindate = None, maxdate = datetime.datetime.now()):
        self.cfg = config
        self._dbmanager = dbmanager
        self._category = category
        self._maxdate = maxdate
        self._is_trending = []
        self._candidates_stats_collections = []

    @property
    def is_trending(self):
        return self._is_trending

    @property
    def candidates_stats_collections(self):
        if not self._candidates_stats_collections:
            try:
                self._candidates_stats_collections = self._dbmanager.get_stats_collections_by_status([Torrent._STATUS_NEW, Torrent._STATUS_FOLLOW], category = self._category)
            except ValueError as err:
                logger_app.info("Zero candidates is empty")
        return self._candidates_stats_collections

    @property
    def maxdate(self):
        return self._maxdate

    def evaluate(self, trend_engine: TrendsEngine, stats_collections: list = None):

        if not stats_collections:
            stats_collections = self.candidates_stats_collections

        nb_to_keep = int(np.ceil(self.cfg.getfloat('trends', 'tau') * len(stats_collections)))

        for sc in stats_collections:
            df = sc.dataframe
            sc.dataframe = df[:self._maxdate]
            
        scores = np.array([trend_engine.score(s) for s in stats_collections])
        item_sorted = np.argsort(scores)[::-1]

        for key, index in enumerate(item_sorted):
            sc = stats_collections[index]
            sc.score = scores[index]
            if key < nb_to_keep:
                self._is_trending.append(sc)   

        return self

    def save_trends(self):
        for stats_col in self._is_trending:
            try:
                self._dbmanager.save_stats_collection_as_trends(stats_col)
                for torrent in stats_col.torrents:
                    logger_app.info("%s / score : %s" % (str(torrent), stats_col.score))
            except Exception as err:
                logger_app.error(err)