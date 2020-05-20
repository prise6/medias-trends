import unittest
import datetime
import hashlib
import numpy as np
from mediastrends import config
from mediastrends.trends.TrendsEngine import ClassicTrendsEngine, NormalizedTrendsEngine
from mediastrends.stats.Stats import Stats
from mediastrends.stats.StatsCollection import StatsCollection
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker
from mediastrends.trends.TrendsManager import TrendsManager


def create_info_hash(content: str):
    return hashlib.sha1(content.encode('utf-8')).hexdigest()


class Engine(unittest.TestCase):

    def setUp(self):
        pub_date = datetime.datetime.now() - datetime.timedelta(days=10)
        valid_date = datetime.datetime.now() - datetime.timedelta(days=5)
        torrent_1 = Torrent(create_info_hash('torrent_1'), 'torrent_1', pub_date=pub_date, size=10)
        torrent_2 = Torrent(create_info_hash('torrent_2'), 'torrent_2', pub_date=pub_date, size=100)
        tracker_A = Tracker('scheme', 'netloc', 'path', 'tracker_A')
        tracker_B = Tracker('scheme', 'netloc', 'path', 'tracker_B')
        self.stats_collections = [
            StatsCollection([
                Stats(torrent_1, tracker_A, leechers=10, seeders=100, completed=50, valid_date=valid_date)
            ]),
            StatsCollection([
                Stats(torrent_2, tracker_A, leechers=10, seeders=200, completed=50, valid_date=valid_date),
                Stats(torrent_2, tracker_A, leechers=10, seeders=100, completed=50, valid_date=valid_date + datetime.timedelta(days=1))
            ]),
            StatsCollection([
                Stats(torrent_1, tracker_A, leechers=30, seeders=100, completed=10, valid_date=valid_date),
                Stats(torrent_1, tracker_A, leechers=300, seeders=120, completed=50, valid_date=valid_date + datetime.timedelta(days=1)),
                Stats(torrent_1, tracker_B, leechers=600, seeders=30, completed=540, valid_date=valid_date + datetime.timedelta(days=1)),
                Stats(torrent_1, tracker_A, leechers=60, seeders=150, completed=100, valid_date=valid_date + datetime.timedelta(days=2)),
                Stats(torrent_1, tracker_A, leechers=100, seeders=200, completed=120, valid_date=valid_date + datetime.timedelta(days=2)),
                Stats(torrent_1, tracker_B, leechers=430, seeders=30, completed=540, valid_date=valid_date + datetime.timedelta(days=2)),
            ])
        ]

    def test_classic_trends_engine_score(self):
        classic_trend_engine = ClassicTrendsEngine(config)
        score_1 = classic_trend_engine.score(self.stats_collections[0])
        self.assertEqual(score_1, 30)

    def test_classic_trends_engine_score_list(self):
        classic_trend_engine = ClassicTrendsEngine(config)
        scores_2 = classic_trend_engine.score_list(self.stats_collections)
        self.assertEqual(scores_2[0], 30)
        self.assertEqual(scores_2[1], 30)
        self.assertEqual(scores_2[2], ((60 + 100) / 2 * .5 + (120 + 100) / 2 * .5) * .5 + (430 + 540) / 2 * .5)

    def test_normalized_trends_engine_score(self):
        normalized_trend_engine = NormalizedTrendsEngine(config)
        normalized_trend_engine._weight_completed = .4
        normalized_trend_engine._weight_leechers = .2
        normalized_trend_engine._weight_seeders = .4
        normalized_trend_engine._lambda = .8

        score_1 = normalized_trend_engine.score(self.stats_collections[0])
        score_2 = normalized_trend_engine.score(self.stats_collections[1])
        score_3 = normalized_trend_engine.score(self.stats_collections[2])

        self.assertEqual(score_1, 100)
        self.assertEqual(score_2, 100)
        self.assertEqual(score_3, 100)

    def test_normalized_trends_engine_score_list_exp(self):
        normalized_trend_engine = NormalizedTrendsEngine(config)
        normalized_trend_engine._weight_completed = .4
        normalized_trend_engine._weight_leechers = .2
        normalized_trend_engine._weight_seeders = .4
        normalized_trend_engine._lambda = .8

        scores = normalized_trend_engine.score_list(self.stats_collections[:2])
        self.assertGreater(scores[0], scores[1])
        self.assertEqual(scores[1], np.round(np.exp(-.8) * 100, 2))

    def test_normalized_trends_engine_score_list(self):
        normalized_trend_engine = NormalizedTrendsEngine(config)
        normalized_trend_engine._weight_completed = .4
        normalized_trend_engine._weight_leechers = .2
        normalized_trend_engine._weight_seeders = .4
        normalized_trend_engine._lambda = .8

        scores = normalized_trend_engine.score_list(self.stats_collections)

        max_tracker_A = np.maximum(
            (10 * .2 + 100 * .4 + 50 * .4) * .8 * np.exp(-.8),
            (80 * .2 + 175 * .4 + 110 * .4) * .8 * np.exp(-.8 * 3)
        )

        max_tracker_B = (430 * .2 + 30 * .4 + 540 * .4) * .8 * np.exp(-.8 * 2)

        self.assertEqual(scores[0], np.round((10 * .2 + 100 * .4 + 50 * .4) * .8 * np.exp(-.8) / max_tracker_A * 100, 2))
        self.assertEqual(scores[1], np.round((10 * .2 + 100 * .4 + 50 * .4) * .8 * np.exp(-.8 * 2) / max_tracker_A * 100, 2))
        self.assertEqual(
            scores[2],
            np.round(
                50 * (80 * .2 + 175 * .4 + 110 * .4) * .8 * np.exp(-.8 * 3) / max_tracker_A
                + 50 * (430 * .2 + 30 * .4 + 540 * .4) * .8 * np.exp(-.8 * 2) / max_tracker_B,
                2
            )
        )


class Manager(unittest.TestCase):

    def setUp(self):
        pub_date = datetime.datetime.now() - datetime.timedelta(days=10)
        valid_date = datetime.datetime.now() - datetime.timedelta(days=5)
        torrent_1 = Torrent(create_info_hash('torrent_1'), 'torrent_1', pub_date=pub_date, size=10)
        tracker_A = Tracker('scheme', 'netloc', 'path', 'tracker_A')
        self.stats_collections = [
            StatsCollection([
                Stats(torrent_1, tracker_A, leechers=10, seeders=100, completed=50, valid_date=valid_date)
            ]),
            StatsCollection([])
        ]

    def test_empty_stats_collections(self):
        stats_collections = []

        trends_manager = TrendsManager(config, None, None)
        normalized_trend_engine = NormalizedTrendsEngine(config)
        trends_manager.evaluate(normalized_trend_engine, stats_collections)

        self.assertEqual(len(trends_manager.is_trending), 0)

    def test_empty_stats_collections_no_stats(self):
        stats_collections = [StatsCollection([])]

        trends_manager = TrendsManager(config, None, None)
        normalized_trend_engine = NormalizedTrendsEngine(config)
        trends_manager.evaluate(normalized_trend_engine, stats_collections)

        self.assertEqual(len(trends_manager.is_trending), 0)

    def test_stats_collections_with_and_without_stats(self):

        trends_manager = TrendsManager(config, None, None)
        normalized_trend_engine = NormalizedTrendsEngine(config)
        trends_manager.evaluate(normalized_trend_engine, self.stats_collections)

        self.assertEqual(len(trends_manager.is_trending), 1)

    def test_date_parameters(self):
        max_date = datetime.datetime.now() - datetime.timedelta(days=20)

        trends_manager = TrendsManager(config, None, None)
        trends_manager._max_date = max_date
        trends_manager._min_date = max_date - datetime.timedelta(days=31)
        normalized_trend_engine = NormalizedTrendsEngine(config)
        trends_manager.evaluate(normalized_trend_engine, self.stats_collections)

        self.assertEqual(len(trends_manager.is_trending), 0)

    def test_date_parameters_equal(self):
        max_date = self.stats_collections[0].stats[0].valid_date
        trends_manager = TrendsManager(config, None, None)
        trends_manager._max_date = max_date
        trends_manager._min_date = max_date - datetime.timedelta(days=31)
        normalized_trend_engine = NormalizedTrendsEngine(config)

        trends_manager._max_date = max_date
        trends_manager._min_date = max_date - datetime.timedelta(days=31)

        trends_manager.evaluate(normalized_trend_engine, self.stats_collections)
        self.assertEqual(len(trends_manager.is_trending), 1)
