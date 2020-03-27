import datetime
import pandas as pd
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Page import Page


class StatsCollection():

    def __init__(self, stats: list):
        self._stats = stats
        self._dataframe = None

    @property
    def stats(self):
        return self._stats

    @property
    def dataframe(self):
        if not self._dataframe:
            self.create_dataframe()
        return self._dataframe

    def extend(self, stats_collection):
        if not stats_collection.__class__.__name__ == self.__class__.__name__:
            raise ValueError("stats_collection argument must be instance of StatsCollection")
        self._stats.extend(stats_collection.stats)
        self._dataframe = None
        return self

    def __add__(self, stats_collection):
        return self.extend(stats_collection)

    def count(self):
        return len(self._stats)

    def is_empty(self):
        return self.count() == 0

    def create_dataframe(self):
        self._dataframe = pd.DataFrame()
        if not self.is_empty():
            self._dataframe = pd.DataFrame.from_dict([s.to_dict() for s in self._stats]).set_index('valid_date').sort_values('valid_date')
        return self

    def is_trending(self):
        """
        Function more complex to move later
        """
        leecher_trend = False
        completed_trend = False
        
        if self.is_empty():
            return False

        self.create_dataframe()

        leecher_trend = self._dataframe.groupby(pd.Grouper(freq = 'D')).mean().tail(1).leechers.item() > 10
        completed_trend = self._dataframe.groupby([pd.Grouper(freq = 'D'), pd.Grouper('tracker_name')]).mean().groupby('valid_date').sum().tail(1).completed.item() > 20

        return leecher_trend and completed_trend

    def __str__(self):
        if self.is_empty():
            r = "Empty stats set"
        else:
            r = "Count: %s \nLast stats: %s" % (self.count(), self._stats[-1])

        return r

    


    
