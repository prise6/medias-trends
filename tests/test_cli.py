import datetime
import contextlib
import io
import unittest
from unittest.mock import patch

import mediastrends.cli as cli


class TestCLI(unittest.TestCase):

    CLI_CALL = 'mediastrends'
    TASKS = [
        'mediastrends.cli.torrents_add',
        'mediastrends.cli.compute_trending',
        'mediastrends.cli.torrents_stats',
        'mediastrends.cli.update_status',
        'mediastrends.cli.get_trending',
        'mediastrends.cli.reset_tables',
        'mediastrends.cli.reset_database',
        'mediastrends.cli.sqlite_backup',
        'mediastrends.cli.load_sqlite_backup'
    ]

    INDEXERS_CONFIG = {
        "indexer_1": {
            "movies": {
                "active": True,
                "action": "search",
                "params": {"cat": 102183}
            },
            "wrong_cat": {
                "active": True
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

    @classmethod
    def setUpClass(cls):
        cls.patches = []
        cls.mocks = {}
        for task in cls.TASKS:
            current_patch = patch('%s' % task)
            print(current_patch)
            cls.patches.append(current_patch)
            cls.mocks[task.split('.').pop()] = current_patch.start()
            print(cls.mocks[task.split('.').pop()])

        populate_config_patch = patch('mediastrends.tools.config.populate_config')
        cls.patches.append(populate_config_patch)
        cls.mocks['populate_config'] = populate_config_patch.start()

        indexers_patch = patch.dict('mediastrends.indexers_config', cls.INDEXERS_CONFIG, clear=True)
        cls.patches.append(indexers_patch)
        cls.mocks['indexers_patch'] = indexers_patch.start()

    @classmethod
    def tearDownClass(cls):
        patch.stopall()

    def test_torrents_trends_get_parser(self):
        parser = cli.TorrentsTrendsGetParser()
        args = '-c movies series unknown -di 202004011200 -dx 202004021200'.split(' ')
        parser.execute(args)
        self.assertTrue(self.mocks['get_trending'].called)
        self.assertEqual(parser.parsed_args_dict.get('category'), ['movies', 'series', 'unknown'])
        self.assertIsInstance(parser.parsed_args_dict.get('mindate'), datetime.datetime)
        self.assertIsInstance(parser.parsed_args_dict.get('maxdate'), datetime.datetime)

    def test_torrents_trends_compute_parser(self):
        parser = cli.TorrentsTrendsComputeParser()
        args = '-c movies series'.split(' ')
        parser.execute(args)
        self.assertTrue(self.mocks['compute_trending'].called)
        self.assertEqual(parser.parsed_args_dict.get('category'), ['movies', 'series'])

    def test_torrents_add_parser(self):
        parser = cli.TorrentsAddParser()
        args = '-c movies -i indexer_1'.split(' ')
        parser.execute(args)
        self.assertTrue(self.mocks['torrents_add'].called)
        self.assertEqual(parser.parsed_args_dict.get('category'), ['movies'])
        self.assertEqual(parser.parsed_args_dict.get('indexer'), 'indexer_1')

    def test_torrents_stats_parser(self):
        parser = cli.TorrentsStatsParser()
        args = '-c movies -t ygg'.split(' ')
        parser.execute(args)
        self.assertTrue(self.mocks['torrents_stats'].called)
        self.assertEqual(parser.parsed_args_dict.get('category'), ['movies'])
        self.assertEqual(parser.parsed_args_dict.get('tracker_name'), 'ygg')

    def test_torrents_status_parser(self):
        parser = cli.TorrentsStatusParser()
        args = '-c movies series'.split(' ')
        parser.execute(args)
        self.assertTrue(self.mocks['update_status'].called)
        self.assertEqual(parser.parsed_args_dict.get('category'), ['movies', 'series'])

    def test_database_reset_table_parser(self):
        parser = cli.DatabaseResetTableParser()
        args = '-t torrent torrenttracker tracker page stats trends --no-backup'.split(' ')
        parser.execute(args)
        self.assertTrue(self.mocks['reset_tables'].called)
        self.assertEqual(parser.parsed_args_dict.get('tables'), ["torrent", "torrenttracker", "tracker", "page", "stats", "trends"])

    def test_database_reset_db_parser(self):
        parser = cli.DatabaseResetDBParser()
        args = ''
        parser.execute(args)
        self.assertTrue(self.mocks['reset_database'].called)

    def test_database_backup_save_parser(self):
        parser = cli.DatabaseBackupSaveParser()
        args = ''
        parser.execute(args)
        self.assertTrue(self.mocks['sqlite_backup'].called)

    def test_database_backup_load_parser(self):
        parser = cli.DatabaseBackupLoadParser()
        args = '-d 20200401-1100'.split(' ')
        parser.execute(args)
        self.assertTrue(self.mocks['load_sqlite_backup'].called)
        self.assertEqual(parser.parsed_args_dict.get('backup_date'), '20200401-1100')

    @patch('mediastrends.tools.config.read_indexers_file', return_value=INDEXERS_CONFIG)
    def test_main_cli_correct(self, mock):
        parser = cli.MediasTrendsCLI()
        args = '-vvvvv --config-dir ./configdir --mode test torrents add -c movies -i indexer_1'
        parser.execute(args.split(' '))
        self.assertTrue(self.mocks['torrents_add'].called)
        self.assertEqual(parser.parsed_args_dict.get('verbose'), 5)
        self.assertEqual(parser.parsed_args_dict.get('config_dir'), './configdir')
        self.assertEqual(parser.parsed_args_dict.get('mode'), 'test')

    @patch('mediastrends.tools.config.read_indexers_file', return_value=INDEXERS_CONFIG)
    def test_main_cli_task_not_defined(self, mock):
        parser = cli.MediasTrendsCLI()
        self.mocks['torrents_add'].side_effect = [NotImplementedError(), None]
        args = '-vvvvv --config-dir ./configdir --mode test torrents add -c movies -i indexer_1'.split(' ')
        with self.assertRaises(NotImplementedError):
            parser.execute(args)

    def test_main_cli_argument_error(self):
        parser = cli.MediasTrendsCLI()
        args = '-vvvvv torrent'.split(' ')
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                parser.execute(args)
        self.assertEqual(cm.exception.code, 2)
