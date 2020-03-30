import numpy as np
import datetime
from mediastrends import logger_app
from mediastrends.database.DbManager import DbManager
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Torrent import Torrent
from mediastrends.stats import StatsCollection
from mediastrends.trends.TrendsEngine import TrendsEngine

class TrendsManager():

    def __init__(self, config, dbmanager: DbManager, category: list = None, maxdate = datetime.datetime.now()):
        self.cfg = config
        self._dbmanager = dbmanager
        self._category = category
        self._maxdate = maxdate
        self._trending_torrents = None
        self._is_trending = []
        self._is_not_trending = []

    @property
    def is_trending(self):
        return self._is_trending

    @property
    def is_not_trending(self):
        return self._is_not_trending

    @property
    def maxdate(self):
        return self._maxdate

    def evaluate(self, stats_collections: list, trend_engine: TrendsEngine = None):

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
            else:
                self._is_not_trending.append(sc)        

        return self

    def save_trends(self):
        for stats_col in self._is_trending:
            try:
                self._dbmanager.save_stats_collection_as_trends(stats_col)
                for torrent in stats_col.torrents:
                    logger_app.info("%s / score : %s" % (str(torrent), stats_col.score))
            except Exception as err:
                logger_app.error(err)