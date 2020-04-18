import pandas as pd
import logging
import numpy as np
from typing import List
from abc import ABC, abstractmethod
from mediastrends.stats import StatsCollection

logger = logging.getLogger(__name__)


class TrendsEngine(ABC):

    @abstractmethod
    def score_list(self, stats_collections: List[StatsCollection]) -> List[float]:
        return

    @abstractmethod
    def score(self, stats_collection: StatsCollection) -> float:
        return


class ClassicTrendsEngine(TrendsEngine):

    def score_list(self, stats_collections: List[StatsCollection]):
        return [self.score(sc) for sc in stats_collections]

    def score(self, stats_collection: StatsCollection):
        leecher_trend = False
        completed_trend = False

        if stats_collection.is_empty():
            logger.warning('stats collection is empty')
            return 0

        # stats_collection.create_dataframe()
        dataframe = stats_collection.dataframe

        # leecher_trend = dataframe.groupby(pd.Grouper(freq='D')).mean().tail(1).leechers.item()
        intermediaire = dataframe.groupby([pd.Grouper(freq='D'), pd.Grouper('tracker_name')]).mean().groupby('valid_date').mean().tail(1)
        completed_trend = intermediaire.completed.item()
        leecher_trend = intermediaire.leechers.item()

        return np.around(0.5 * leecher_trend + 0.5 * completed_trend, 2)


class NormalizedTrendsEngine(TrendsEngine):

    def score_list(self, stats_collections: List[StatsCollection]) -> List[float]:

        concat_df = None
        for sc_index, sc in enumerate(stats_collections):
            sc_df = sc.dataframe
            sc_df['sc_index'] = sc_index
            if sc_index > 0:
                concat_df = pd.concat([concat_df, sc_df])
            else:
                concat_df = sc_df

        score_df = concat_df.groupby([pd.Grouper('sc_index'), pd.Grouper(freq='D'), pd.Grouper('tracker_name')]).mean()
        score_df['score'] = score_df['leechers'] * 0.5 + score_df['completed'] * 0.5
        score_df = score_df.reset_index()
        # score_df = score_df.reset_index(['valid_date', 'sc_index'])
        score_max_df = score_df.groupby(['tracker_name']).max().rename(columns={'score': 'score_max'})[['score_max']]
        score_df = score_df.merge(score_max_df, how="inner", on=["tracker_name"], validate="many_to_one")
        score_df['score_normalized'] = score_df['score'] / score_df['score_max'] * 100
        score_df = score_df.groupby([pd.Grouper('sc_index'), pd.Grouper('tracker_name')]).last().groupby(['sc_index'])[['score_normalized']].mean().round(2)

        return score_df.score_normalized.to_list()

    def score(self, stats_collection: StatsCollection):
        logger.warning('NormalizedTrendsEngine must have other stats_collection to score more precisely')
        return self.score_list([stats_collection]).pop()
