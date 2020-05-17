import datetime
import logging
import numpy as np
from mediastrends import STATUS_NAME
from mediastrends.database.DbManager import DbManager
from mediastrends.trends.TrendsEngine import TrendsEngine

logger = logging.getLogger(__name__)


class TrendsManager():

    def __init__(self, config, dbmanager: DbManager, category: list = None):
        self.cfg = config
        self._dbmanager = dbmanager
        self._category = category
        self._is_trending = []
        self._candidates_stats_collections = []

        self._max_date = self.cfg.getdatetime('trends_manager', 'max_date', fallback=datetime.datetime.now())
        self._delta_days = self.cfg.getint('trends_manager', 'delta_days', fallback=31)
        self._min_date = self.cfg.getdatetime('trends_manager', 'min_date', fallback=self._max_date - datetime.timedelta(days=self._delta_days))
        self._torrents_status = [STATUS_NAME[s] for s in self.cfg.getlist('trends_manager', 'torrents_status', fallback=['new', 'follow'])]
        self._tau = self.cfg.getfloat('trends_manager', 'tau', fallback=0.2)
        self._max_trendings = self.cfg.getint('trends_manager', 'max_trendings', fallback=50)

    @property
    def is_trending(self):
        return self._is_trending

    @property
    def candidates_stats_collections(self):
        if not self._candidates_stats_collections:
            try:
                self._candidates_stats_collections = self._dbmanager.get_stats_collections_by_status(
                    status=self._torrents_status,
                    category=self._category,
                    min_date=self._min_date,
                    max_date=self._max_date
                )
            except ValueError:
                logger.warning("Candidates stats collections are empty")
        return self._candidates_stats_collections

    @property
    def maxdate(self):
        return self._maxdate

    def evaluate(self, trend_engine: TrendsEngine, stats_collections: list = None):

        if not stats_collections:
            stats_collections = self.candidates_stats_collections

        final_stats_collections = []
        for sc in stats_collections:
            if not sc.is_empty():
                df = sc.dataframe
                sc.dataframe = df[:self._max_date]
                final_stats_collections.append(sc)

        nb_to_keep = int(np.minimum(np.ceil(self._tau * len(final_stats_collections)), self._max_trendings))
        logger.debug("Number of torrents to keep: %s", nb_to_keep)

        if nb_to_keep == 0:
            return self

        scores = np.array(trend_engine.score_list(final_stats_collections))
        item_sorted = np.argsort(scores)[::-1]

        for key, index in enumerate(item_sorted):
            sc = final_stats_collections[index]
            sc.score = scores[index]
            if key < nb_to_keep:
                self._is_trending.append(sc)

        return self

    def save_trends(self):
        for stats_col in self._is_trending:
            try:
                self._dbmanager.save_stats_collection_as_trends(stats_col)
                for torrent in stats_col.torrents:
                    logger.debug("%s / score : %s" % (str(torrent), stats_col.score))
            except Exception as err:
                logger.error(err)
