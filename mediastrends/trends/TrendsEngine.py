import pandas as pd
from abc import ABC, abstractmethod, abstractstaticmethod
from mediastrends.stats import StatsCollection

class TrendsEngine(ABC):

    @abstractmethod
    def score(self, stats_collection: StatsCollection) -> float:
        return

class ClassicTrendsEngine(TrendsEngine):

    def score(self, stats_collection: StatsCollection):
        leecher_trend = False
        completed_trend = False
        
        if stats_collection.is_empty():
            return 0

        # stats_collection.create_dataframe()
        dataframe = stats_collection.dataframe

        leecher_trend = dataframe.groupby(pd.Grouper(freq = 'D')).mean().tail(1).leechers.item()
        completed_trend = dataframe.groupby([pd.Grouper(freq = 'D'), pd.Grouper('tracker_name')]).mean().groupby('valid_date').sum().tail(1).completed.item()

        return 0.5*leecher_trend+0.5*completed_trend
