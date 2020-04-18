import unittest
import datetime
import hashlib
import numpy as np
from mediastrends.trends.TrendsEngine import ClassicTrendsEngine, NormalizedTrendsEngine
from mediastrends.stats.Stats import Stats
from mediastrends.stats.StatsCollection import StatsCollection
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker


class TrendsEngine(unittest.TestCase):

    def create_info_hash(self, content: str):
        return hashlib.sha1(content.encode('utf-8')).hexdigest()

    def setUp(self):
        pub_date = datetime.datetime.now() - datetime.timedelta(days=10)
        valid_date = datetime.datetime.now() - datetime.timedelta(days=5)
        torrent_1 = Torrent(self.create_info_hash('torrent_1'), 'torrent_1', pub_date=pub_date, size=10)
        tracker_A = Tracker('scheme', 'netloc', 'path', 'tracker_A')
        tracker_B = Tracker('scheme', 'netloc', 'path', 'tracker_B')
        self.stats_collections = [
            StatsCollection([
                Stats(torrent_1, tracker_A, leechers=10, seeders=100, completed=50, valid_date=valid_date),
                Stats(torrent_1, tracker_A, leechers=20, seeders=90, completed=60, valid_date=valid_date + datetime.timedelta(days=1)),
                Stats(torrent_1, tracker_A, leechers=15, seeders=80, completed=70, valid_date=valid_date + datetime.timedelta(days=2)),
                Stats(torrent_1, tracker_A, leechers=10, seeders=70, completed=80, valid_date=valid_date + datetime.timedelta(days=3)),
            ]),
            StatsCollection([
                Stats(torrent_1, tracker_A, leechers=30, seeders=100, completed=10, valid_date=valid_date),
                Stats(torrent_1, tracker_A, leechers=300, seeders=120, completed=50, valid_date=valid_date + datetime.timedelta(days=1)),
                Stats(torrent_1, tracker_A, leechers=60, seeders=150, completed=100, valid_date=valid_date + datetime.timedelta(days=2)),
                Stats(torrent_1, tracker_A, leechers=100, seeders=200, completed=120, valid_date=valid_date + datetime.timedelta(days=2)),
            ]),
            StatsCollection([
                Stats(torrent_1, tracker_A, leechers=30, seeders=100, completed=10, valid_date=valid_date),
                Stats(torrent_1, tracker_A, leechers=300, seeders=120, completed=50, valid_date=valid_date + datetime.timedelta(days=1)),
                Stats(torrent_1, tracker_A, leechers=60, seeders=150, completed=100, valid_date=valid_date + datetime.timedelta(days=2)),
                Stats(torrent_1, tracker_A, leechers=100, seeders=200, completed=120, valid_date=valid_date + datetime.timedelta(days=2)),
                Stats(torrent_1, tracker_B, leechers=430, seeders=30, completed=540, valid_date=valid_date + datetime.timedelta(days=2)),
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

    def test_classic_trends_engine(self):
        classic_trend_engine = ClassicTrendsEngine()
        score_1 = classic_trend_engine.score(self.stats_collections[0])
        self.assertEqual(score_1, 45)

        scores_2 = classic_trend_engine.score_list(self.stats_collections)
        self.assertEqual(scores_2[0], score_1)
        self.assertEqual(scores_2[1], np.round((60 + 100) / 2 * .5 + (120 + 100) / 2 * .5))
        self.assertEqual(scores_2[2], ((60 + 100) / 2 * .5 + (120 + 100) / 2 * .5) * .5 + (430 + 540) / 2 * .5)

    def test_normalized_trends_engine(self):
        normalized_trend_engine = NormalizedTrendsEngine()

        scores = normalized_trend_engine.score_list(self.stats_collections)

        max_tracker_A = 175
        max_tracker_B = 570
        self.assertEqual(scores[0], np.round(45 / max_tracker_A * 100, 2))
        self.assertEqual(scores[1], np.round((95 / max_tracker_A) * 100, 2))
        self.assertEqual(scores[2], np.round(((95 / max_tracker_A) * .5 + ((430 + 540) / 2) / max_tracker_B * .5) * 100, 2))
        self.assertEqual(scores[3], np.round(((95 / 175) * .5 + ((430 + 540) / 2) / max_tracker_B * .5) * 100, 2))

        score_1 = normalized_trend_engine.score(self.stats_collections[0])
        self.assertEqual(score_1, 100)
