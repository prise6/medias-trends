import unittest
import datetime
import requests
from unittest.mock import patch, PropertyMock, MagicMock
from mediastrends import db_factory
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.tasks.torrents import (torrents_add,
                                         create_torznab_from_cli_params,
                                         elements_from_torznab_result,
                                         torrents_stats,
                                         torrents_stats_with_tracker)
from mediastrends.torznab.TorznabRSS import TorznabJackettResult
from mediastrends.torrent.Tracker import UdpTracker
from mediastrends.torrent.Torrent import Torrent


class TorentsTasks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        indexers_config = {
            "indexer_1": {
                "movies": {
                    "active": True,
                    "action": "search",
                    "params": {"cat": 102183}
                },
                "wrong_cat": {
                    "active": False,
                    "action": "search"
                }
            },
            "indexer_2": {
                "series": {
                    "active": True,
                    "action": "search",
                    "params": {"cat": 102185}
                }
            }
        }
        cls.indexers_patch = patch.dict('mediastrends.indexers_config', indexers_config, clear=True)
        cls.indexers_mock = cls.indexers_patch.start()

        trackers_config = {
            'tracker_1': {
                'active': True,
                'scheme': 'http',
                'netloc': 'netloc:8080',
            },
            'tracker_2': {
                'active': True,
                'scheme': 'udp',
                'netloc': 'netloc:6060',
            },
            'tracker_3': {
                'active': False,
                'scheme': 'udp',
                'netloc': 'netloc:5217',
            },
        }
        cls.trackers_patch = patch.dict('mediastrends.trackers_config', trackers_config, clear=True)
        cls.trackers_mock = cls.trackers_patch.start()

        # db
        db_factory.defaut_instance = 'sqlite-app-test'
        PDbManager.create_database(db_factory.get_instance())

    @classmethod
    def tearDownClass(cls):
        patch.stopall()
        PDbManager.drop_database(db_factory.get_instance())

    def setUp(self):
        # torznab_input
        self.result_torznab_input = [{
            'title': 'Test 1 titre',
            'guid': 'test1guid',
            'pubDate': datetime.datetime.now(),
            'category': 2000,
            'link': 'link-to-torrentfile-1',
            'infohash': '85be94b120becfb44f94f97779c61633c7647629',
            'size': 1223
        }, {
            'title': 'Test 2 titre',
            'guid': 'test2guid',
            'pubDate': datetime.datetime.now(),
            'category': 5000,
            'link': 'link-to-torrentfile-2',
            'infohash': '85be94b120becfb44f94f97779c61633c7647628',
            'size': 4000,
            'imdb': '2438644'
        }]

        # rss_parser items
        self.rss_parser_items = [TorznabJackettResult(r) for r in self.result_torznab_input]

    def tearDown(self):
        patch.stopall()


class TorrentsAdd(TorentsTasks):

    def test_create_torznab_from_cli_params(self):
        client = create_torznab_from_cli_params("indexer_1", "movies")
        self.assertEqual(client.action, "search")
        self.assertEqual(client.indexer, "indexer_1")
        self.assertEqual(client._params.get('cat'), 102183)

        client = create_torznab_from_cli_params("indexer_2", "series")
        self.assertEqual(client.action, "search")
        self.assertEqual(client.indexer, "indexer_2")
        self.assertEqual(client._params.get('cat'), 102185)

        with self.assertRaises(Exception):
            client = create_torznab_from_cli_params("yggtorren", "movies")
        with self.assertRaises(Exception):
            client = create_torznab_from_cli_params("indexer_1", "wrong_cat")

    def test_elements_from_torznab_result(self):
        torznab_result = self.rss_parser_items[0]
        with patch('mediastrends.torrent.Torrent.TorrentFile.extras', new_callable=PropertyMock) as mock_tf:
            mock_tf.return_value = {'tracker_urls': None}
            elements = elements_from_torznab_result(torznab_result)
            self.assertFalse(elements['keep'])

            mock_tf.return_value = {'tracker_urls': ['http://netloc:8080']}
            elements = elements_from_torznab_result(torznab_result)
            self.assertTrue(elements['keep'])
            self.assertEqual(elements['trackers'][0].name, 'tracker_1')
            self.assertEqual(elements['trackers'][0].netloc, 'netloc:8080')
            self.assertEqual(elements['torrent'].name, torznab_result.get('title'))
            self.assertEqual(elements['torrent'].imdb_id, torznab_result.get('imdb'))

            mock_tf.return_value = {'tracker_urls': ['udp://netloc:5217']}
            elements = elements_from_torznab_result(torznab_result)
            self.assertFalse(elements['keep'])

    @patch('mediastrends.torrent.Torrent.TorrentFile.extras', new_callable=PropertyMock)
    @patch("mediastrends.torznab.TorznabClient.TorznabJackettClient.get_rss_content", return_value="")
    @patch("mediastrends.tasks.torrents.TorznabJackettRSS", autospec=True)
    def test_torrents_add(self, mock_rss, mock_client, mock_tf):
        instance_rss = mock_rss.return_value
        instance_rss.items = self.rss_parser_items
        instance_rss.process_items.return_value = True
        mock_tf.return_value = {'tracker_urls': ['http://netloc:8080']}
        nb_torrents_added = torrents_add(False, "indexer_1", ["movies"])
        self.assertTrue(mock_client.called)
        self.assertTrue(mock_rss.called)
        self.assertTrue(mock_tf.called)
        self.assertEqual(nb_torrents_added, 2)

        self.assertEqual(PDbManager.get_tracker_by_name("tracker_1").netloc, "netloc:8080")
        self.assertEqual(PDbManager.get_torrent_by_hash("85be94b120becfb44f94f97779c61633c7647628").imdb_id, "2438644")

        nb_torrents_added = torrents_add(False, "indexer_1", ["series"])
        self.assertEqual(nb_torrents_added, 0)


class TorrentsStats(TorentsTasks):

    def setUp(self):
        super().setUp()

        # init mock tracker
        self.result_of_scrape = {'85be94b120becfb44f94f97779c61633c7647629': {
            'complete': 10,
            'downloaded': 100,
            'incomplete': 32,
        }}

        mock_tracker = UdpTracker(scheme="udp", netloc="netloc:6060", name="tracker_2", path="")
        # type(mock_tracker).name = PropertyMock(return_value="tracker_name")
        mock_tracker.scrape = MagicMock(return_value=self.result_of_scrape)
        self.mock_tracker = mock_tracker

        # init db
        self.fake_torrent = Torrent(
            info_hash="85be94b120becfb44f94f97779c61633c7647629",
            name='Test 1 titre',
            pub_date=datetime.datetime.now(),
            size=1220
        )
        PDbManager.save_torrent_tracker(self.fake_torrent, self.mock_tracker)

    def test_torrents_stats_with_tracker(self):
        nb_stats = torrents_stats_with_tracker(self.mock_tracker)
        self.assertEqual(nb_stats, 1)
        stats_collec = PDbManager.get_stats_collection_by_torrent(self.fake_torrent)
        self.assertEqual(nb_stats, stats_collec.count())
        self.assertEqual(stats_collec.stats[0].leechers, 32)
        self.assertEqual(stats_collec.stats[0].seeders, 10)
        self.assertEqual(stats_collec.stats[0].completed, 100)
        self.assertEqual(stats_collec.stats[0].torrent.name, self.fake_torrent.name)
        self.assertEqual(stats_collec.stats[0].tracker.name, self.mock_tracker.name)

        nb_stats = torrents_stats_with_tracker(self.mock_tracker, [0])
        self.assertEqual(nb_stats, 0)

        nb_stats = torrents_stats_with_tracker(self.mock_tracker, [])
        self.assertEqual(nb_stats, 0)

    @patch('mediastrends.stats.StatsScraper.run')
    def test_torrents_stats_with_tracker_error(self, mock_run):
        mock_run.side_effect = [OSError, requests.exceptions.RequestException]
        nb_stats = torrents_stats_with_tracker(self.mock_tracker)
        self.assertEqual(nb_stats, 0)
        nb_stats = torrents_stats_with_tracker(self.mock_tracker)
        self.assertEqual(nb_stats, 0)

    @patch('mediastrends.tasks.torrents.torrents_stats_with_tracker', return_value=1)
    def test_torrents_stats(self, mock_fn):
        nb_stats = torrents_stats(False, "tracker_1", category=['movies'])
        self.assertEqual(nb_stats, 1)
        nb_stats = torrents_stats(False, "tracker_3", category=['movies'])
        self.assertEqual(nb_stats, 0)
        with self.assertRaises(AssertionError):
            nb_stats = torrents_stats(False, "tracker_xx", category=['movies'])
        with self.assertRaises(KeyError):
            nb_stats = torrents_stats(False, "tracker_1", category=['wrong_category'])
        with self.assertRaises(AssertionError):
            nb_stats = torrents_stats(False, "tracker_1", category='not_a_list')
