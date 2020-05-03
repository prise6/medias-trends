import datetime
from typing import Union
from abc import ABC, abstractmethod, abstractstaticmethod
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.IMDBObject import Movie
from mediastrends.torrent.Page import Page
from mediastrends.stats.Stats import Stats
from mediastrends.stats.StatsCollection import StatsCollection


class DbManager(ABC):
    """Need to be more abstract if not using peewee
    """

    def __init__(self, config):
        self.cfg = config

    @abstractstaticmethod
    def create_database(db_connection):
        return

    @abstractstaticmethod
    def drop_database(db_connection):
        return

    @abstractstaticmethod
    def db_to_torrent(db_torrent):
        return

    @abstractstaticmethod
    def db_to_tracker(db_tracker):
        return

    @abstractstaticmethod
    def db_to_page(db_page):
        return

    @abstractstaticmethod
    def db_to_stats(db_stats):
        return

    @abstractstaticmethod
    def db_to_movie(db_imdb_obj):
        return

    @abstractstaticmethod
    def tracker_to_db(tracker: Tracker, update=False):
        return

    @abstractstaticmethod
    def torrent_to_db(torrent: Torrent, update=False):
        return

    @abstractstaticmethod
    def imdb_object_to_db(obj: Union[Movie], update=False):
        return

    @classmethod
    def movie_to_db(cls, movie: Movie, update=False):
        if not isinstance(movie, Movie):
            raise TypeError("Movie must be instance of Movie")
        return cls.imdb_object_to_db(movie, update)

    @abstractstaticmethod
    def update(obj):
        return

    @abstractstaticmethod
    def save_page(page: Page, torrent: Torrent, tracker: Tracker):
        return

    @abstractstaticmethod
    def save_torrent_tracker(torrent: Torrent, tracker: Tracker):
        return

    @abstractstaticmethod
    def save_stats(stats: Stats):
        return

    @abstractstaticmethod
    def save_stats_collection_as_trends(stats_collection: StatsCollection):
        return

    @abstractstaticmethod
    def get_torrent_by_hash(info_hash: str):
        return

    @abstractstaticmethod
    def get_tracker_by_name(name: str):
        return

    @abstractstaticmethod
    def get_stats_collection_by_torrent(torrent: Torrent):
        return

    @abstractmethod
    def get_stats_collections_by_status(status: list, category: list = None, min_date=None, max_date=datetime.datetime.now()):
        """Fetch StatsCollection list by torrent

        This function return a list of StatsCollection object for every torrent with status.

        Args:
            status (list): list of torrent status
            category (list, optional): list of torrent category. Defaults to None.
            min_date (datetime.datetime, optional): minimum date of stats. Defaults to None.
            max_date (datetime.datetime, optional): maximum date of stats. Defaults to datetime.datetime.now().
        """
        return

    @abstractstaticmethod
    def get_torrents_by_status(status: int, category: list = None):
        return

    @abstractstaticmethod
    def get_torrents_by_tracker(tracker: Tracker, status: list, category: list = None):
        return

    @abstractstaticmethod
    def get_trending_torrents_by_category(category: list = None, min_date=None, max_date=None):
        return

    @abstractstaticmethod
    def get_trending_movies(min_date=None, max_date=None):
        return

    @classmethod
    def get_stats_collection(cls, obj):
        if isinstance(obj, Torrent):
            stats_collection = cls.get_stats_collection_by_torrent(obj)
        elif isinstance(obj, list):
            stats_collection = StatsCollection([])
            for item in obj:
                stats_collection += cls.get_stats_collection(item)
        else:
            raise ValueError("Not implemented yet.")
        return stats_collection
