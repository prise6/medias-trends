import unittest
import datetime
import random
from peewee import sqlite3
from mediastrends import db_factory
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.IMDBObject import Movie
from mediastrends.stats.Stats import Stats
from mediastrends.stats.StatsCollection import StatsCollection
from mediastrends.database.peewee.PTracker import PTracker
from mediastrends.database.peewee.PTorrent import PTorrent, PTorrentTracker
from mediastrends.database.peewee.PIMDBObject import PIMDBObject
from mediastrends.database.peewee.PStats import PStats
from mediastrends.database.peewee.PTrends import PTrends


def generate_torrents(nb):
    return [Torrent(
        info_hash='%40x' % random.getrandbits(160),
        name="name",
        size=random.randint(200, 5000),
        pub_date=datetime.datetime.now(),
        category=Torrent._CAT_MOVIE
    ) for i in range(nb)]


_TORRENTS = generate_torrents(3)


def setUpModule():
    db_factory.defaut_instance = 'sqlite-app-test'
    PDbManager.create_database(db_factory.get_instance())


def tearDownModule():
    PDbManager.drop_database(db_factory.get_instance())


class InitDb(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.torrents = _TORRENTS
        cls.trackers = [
            Tracker("http", "netloc:8080", "/path", name="tracker_1"),
            Tracker("http", "netloc:8080", "/path", name="tracker_2"),
            Tracker("udp", "netloc:6969", path=None, name="tracker_3")
        ]

        cls.movies = []
        cls.movies.append(Movie(imdb_id="00455"))
        cls.movies[0]._extras.update({'title': 'title_1', 'rating': 10, 'cover_url': 'cover_url_1', 'year': 2018})
        cls.movies.append(Movie(imdb_id="00456"))
        cls.movies[1]._extras.update({'title': 'title_2', 'rating': 5, 'cover_url': 'cover_url_2', 'year': 2020})
        cls.movies.append(Movie(imdb_id="6563"))
        cls.movies[2]._extras.update({'title': 'title_3', 'rating': 0, 'cover_url': 'cover_url_3', 'year': 1999})

        cls.stats = [
            Stats(_TORRENTS[0], cls.trackers[1], valid_date=datetime.datetime.now() - datetime.timedelta(days=2), leechers=30, seeders=10, completed=100),
            Stats(_TORRENTS[0], cls.trackers[1], valid_date=datetime.datetime.now() - datetime.timedelta(days=1), leechers=30, seeders=30, completed=120),
            Stats(_TORRENTS[1], cls.trackers[1], valid_date=datetime.datetime.now(), leechers=10, seeders=30, completed=120),
        ]

        cls.stats_collections = []
        cls.stats_collections.append(StatsCollection(cls.stats))
        cls.stats_collections[0]._score = 20


class TrackerInit(InitDb):

    def test_tracker_to_db(self):
        for tracker in self.trackers:
            db_tracker, created, updated = PDbManager.tracker_to_db(tracker)
            self.assertIsInstance(db_tracker, PTracker)
            self.assertTrue(created)
            self.assertFalse(updated)

    def test_tracker_to_db_already_exist(self):
        db_tracker, created, updated = PDbManager.tracker_to_db(self.trackers[0])

        self.assertIsInstance(db_tracker, PTracker)
        self.assertFalse(created)
        self.assertFalse(updated)


class TorrentInit(InitDb):

    def test_torrent_to_db(self):
        for torrent in self.torrents:
            db_torrent, created, updated = PDbManager.torrent_to_db(torrent)
            self.assertIsInstance(db_torrent, PTorrent)
            self.assertTrue(created)
            self.assertFalse(updated)

    def test_torrent_to_db_already_exist(self):
        torrent = self.torrents[0]
        db_torrent, created, updated = PDbManager.torrent_to_db(torrent)
        self.assertIsInstance(db_torrent, PTorrent)
        self.assertFalse(created)
        self.assertFalse(updated)


class ImdbObjInit(InitDb):

    def test_imdb_object_to_db(self):
        imdb_objs = self.movies
        for imdb_obj in imdb_objs:
            db_imdb_obj, torrents_updated = PDbManager.imdb_object_to_db(imdb_obj)
            self.assertIsInstance(db_imdb_obj, PIMDBObject)
            self.assertEqual(torrents_updated, 0)

    def test_imdb_object_to_db_already_exist(self):
        db_imdb_obj, torrents_updated = PDbManager.imdb_object_to_db(self.movies[0])
        self.assertIsInstance(db_imdb_obj, PIMDBObject)
        self.assertEqual(torrents_updated, 0)

    def test_imdb_object_to_db_with_torrents(self):
        movie = self.movies[0]
        movie.torrents = self.torrents[1:]
        db_imdb_obj, torrents_updated = PDbManager.imdb_object_to_db(movie)
        self.assertIsInstance(db_imdb_obj, PIMDBObject)
        self.assertEqual(torrents_updated, 2)


class UpdateInit(InitDb):

    def test_update_torrent(self):
        db_torrent, updated = PDbManager.update(self.torrents[0])
        self.assertIsInstance(db_torrent, PTorrent)
        self.assertFalse(updated)

        self.torrents[0].name = "name_1"
        db_torrent, updated = PDbManager.update(self.torrents[0])
        self.assertIsInstance(db_torrent, PTorrent)
        self.assertTrue(updated)

    def test_update_tracker(self):
        db_tracker, updated = PDbManager.update(self.trackers[0])
        self.assertIsInstance(db_tracker, PTracker)
        self.assertFalse(updated)

        self.trackers[0]._path = '/path/updated'
        db_tracker, updated = PDbManager.update(self.trackers[0])
        self.assertIsInstance(db_tracker, PTracker)
        self.assertTrue(updated)

    def test_update_movie(self):
        with self.assertRaises(ValueError):
            db_movie, updated = PDbManager.update(self.movies[0])

        db_imdb_obj, torrents_updated = PDbManager.movie_to_db(self.movies[0], update=True)
        self.assertIsInstance(db_imdb_obj, PIMDBObject)


class SpecialSave(InitDb):

    def test_save_torrent_tracker(self):
        torrent = self.torrents[0]
        tracker = self.trackers[0]
        db_torrent_tracker, created, torrent_created, tracker_created = PDbManager.save_torrent_tracker(torrent, tracker)
        self.assertIsInstance(db_torrent_tracker, PTorrentTracker)
        self.assertTrue(created)
        self.assertFalse(torrent_created)
        self.assertFalse(tracker_created)

        db_torrent_tracker_query = PTorrentTracker.select().first()
        self.assertEqual(db_torrent_tracker, db_torrent_tracker_query)

    def test_save_stats(self):
        for stat in self.stats:
            db_stats, created = PDbManager.save_stats(stat)
            self.assertIsInstance(db_stats, PStats)
            self.assertTrue(created)

        db_stats, created = PDbManager.save_stats(self.stats[0])
        self.assertIsInstance(db_stats, PStats)
        self.assertFalse(created)

    def test_save_stats_collection_as_trends(self):
        for stats_collection in self.stats_collections:
            db_trends, created = PDbManager.save_stats_collection_as_trends(stats_collection)
            self.assertIsInstance(db_trends, PTrends)
            self.assertTrue(created)


class GetDb(InitDb):

    def test_get_torrent_by_hash(self):
        torrent = PDbManager.get_torrent_by_hash(self.torrents[2].info_hash)
        self.assertEqual(torrent.info_hash, self.torrents[2].info_hash)
        self.assertEqual(torrent.name, self.torrents[2].name)
        self.assertEqual(torrent.pub_date, self.torrents[2].pub_date)
        self.assertEqual(torrent.size, self.torrents[2].size)
        self.assertEqual(torrent._status, self.torrents[2]._status)
        self.assertEqual(torrent._category, self.torrents[2]._category)

    def test_get_tracker_by_name(self):
        tracker = PDbManager.get_tracker_by_name(self.trackers[2].name)
        self.assertEqual(tracker.name, self.trackers[2].name)
        self.assertEqual(tracker.path, self.trackers[2].path)
        self.assertEqual(tracker.netloc, self.trackers[2].netloc)
        self.assertEqual(tracker.scheme, self.trackers[2].scheme)

    def test_get_stats_collection_by_torrent(self):
        stats_collection = PDbManager.get_stats_collection_by_torrent(self.torrents[0])
        self.assertEqual(stats_collection.count(), 2)

        stats_collection = PDbManager.get_stats_collection_by_torrent(self.torrents[1])
        self.assertEqual(stats_collection.count(), 1)
        self.assertEqual(stats_collection.stats[0].leechers, 10)

        stats_collection = PDbManager.get_stats_collection_by_torrent(self.torrents[2])
        self.assertEqual(stats_collection.count(), 0)

    def test_get_stats_collections_by_status(self):
        max_date = datetime.datetime.now() + datetime.timedelta(days=1)
        stats_collections = PDbManager.get_stats_collections_by_status(Torrent._STATUS_NEW, max_date=max_date)
        # nombre de torrents
        self.assertEqual(len(stats_collections), 3)

        nb_stats = 0
        for stats_collection in stats_collections:
            nb_stats += len(stats_collection.stats)

        self.assertEqual(len(self.stats), nb_stats)

    def test_get_torrents_by_status(self):
        torrents = PDbManager.get_torrents_by_status(Torrent._STATUS_NEW)
        self.assertEqual(len(self.torrents), len(torrents))
        self.assertIsInstance(torrents[0], Torrent)

        with self.assertRaises(ValueError):
            torrents = PDbManager.get_torrents_by_status(Torrent._STATUS_UNFOLLOW)

    def test_get_torrents_by_tracker(self):
        torrents = PDbManager.get_torrents_by_tracker(self.trackers[0])
        self.assertEqual(1, len(torrents))
        self.assertIsInstance(torrents[0], Torrent)

        torrents = PDbManager.get_torrents_by_tracker(self.trackers[2])
        self.assertEqual(torrents, [])

    @unittest.skipIf(sqlite3.sqlite_version_info < (3, 25), "Window function support was first added to SQLite with release version 3.25.0")
    def test_get_trending_torrents_by_category(self):
        torrents = PDbManager.get_trending_torrents_by_category(Torrent._CAT_MOVIE)
        self.assertEqual(2, len(torrents))
        self.assertEqual(self.stats_collections[0]._score, torrents[0][1])

    def test_get_max_trend_date_by_category(self):
        max_date = PDbManager.get_max_trend_date_by_category(Torrent._CAT_MOVIE)
        self.assertGreaterEqual(self.stats[2].valid_date, max_date)
        self.assertGreater(max_date, self.stats[1].valid_date)


def suite(loader):
    suite = unittest.TestSuite()
    suite.addTest(TrackerInit('test_tracker_to_db'))
    suite.addTest(TrackerInit('test_tracker_to_db_already_exist'))
    suite.addTest(TorrentInit('test_torrent_to_db'))
    suite.addTest(TorrentInit('test_torrent_to_db_already_exist'))
    suite.addTest(ImdbObjInit('test_imdb_object_to_db'))
    suite.addTest(ImdbObjInit('test_imdb_object_to_db_already_exist'))
    suite.addTest(ImdbObjInit('test_imdb_object_to_db_with_torrents'))
    suite.addTest(UpdateInit('test_update_torrent'))
    suite.addTest(UpdateInit('test_update_tracker'))
    suite.addTest(UpdateInit('test_update_movie'))
    suite.addTest(SpecialSave('test_save_torrent_tracker'))
    suite.addTest(SpecialSave('test_save_stats'))
    suite.addTest(SpecialSave('test_save_stats_collection_as_trends'))
    suite.addTests(loader.loadTestsFromTestCase(GetDb))

    return suite


def load_tests(loader, standard_test, pattern):
    return suite(loader)
