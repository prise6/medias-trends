import unittest
import datetime
from unittest.mock import patch, PropertyMock
from mediastrends.tasks import (create_torznab_from_cli_params, elements_from_torznab_result)
from mediastrends.torznab.TorznabRSS import TorznabJackettResult


class TorrentsAdd(unittest.TestCase):

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
            },
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

    @classmethod
    def tearDownClass(cls):
        patch.stopall()

    def setUp(self):
        self.result_torznab_input = {
            'title': 'Titre',
            'guid': 'hopeitislinktopage',
            'pubDate': datetime.datetime.now(),
            'category': 2000,
            'link': 'link-to-torrentfile',
            'infohash': '85be94b120becfb44f94f97779c61633c7647629',
            'size': 1223
        }

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
        input_ = self.result_torznab_input
        result = TorznabJackettResult(input_)
        with patch('mediastrends.torrent.Torrent.TorrentFile.extras', new_callable=PropertyMock) as mock_tf:
            mock_tf.return_value = {'tracker_urls': None}
            elements = elements_from_torznab_result(result)
            self.assertFalse(elements['keep'])

            mock_tf.return_value = {'tracker_urls': ['http://netloc:8080']}
            elements = elements_from_torznab_result(result)
            self.assertTrue(elements['keep'])
            self.assertEqual(elements['tracker'].name, 'tracker_1')
            self.assertEqual(elements['tracker'].netloc, 'netloc:8080')

            mock_tf.return_value = {'tracker_urls': ['udp://netloc:5217']}
            elements = elements_from_torznab_result(result)
            self.assertFalse(elements['keep'])
