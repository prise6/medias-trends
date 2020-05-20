import pandas as pd


class StatsCollection():

    def __init__(self, stats: list):
        self._stats = stats
        self._dataframe = None
        self._valid_date = None
        self._score = None

    @property
    def stats(self):
        return self._stats

    @property
    def dataframe(self):
        if not self.is_empty() and self._dataframe is None:
            self.create_dataframe()
        return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe):
        self._dataframe = dataframe
        return self

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score
        return self

    @property
    def valid_date(self):
        if not self._valid_date:
            self._valid_date = self.dataframe.index.max().to_pydatetime()
        return self._valid_date

    @property
    def torrents(self):
        id_torrents = []
        torrents = []
        for s in self._stats:
            if id(s.torrent) not in id_torrents:
                torrents.append(s.torrent)
                id_torrents.append(id(s.torrent))
        return torrents

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
        if not self.is_empty():
            self._dataframe = pd.DataFrame.from_dict([s.to_dict() for s in self._stats]).set_index('valid_date').sort_values('valid_date')
        return self

    def __str__(self):
        if self.is_empty():
            r = "Empty stats set"
        else:
            r = "Count: %s \nLast stats: %s" % (self.count(), self._stats[-1])
            r += "\nSample torrent: %s" % (self._stats[-1].torrent.name)

        return r
