import sys
import logging
from abc import ABC, abstractmethod
import argparse
import datetime

import mediastrends.tools.config as cfg
from mediastrends import config, trackers_config, indexers_config, db_factory
from mediastrends.tasks.torrents import torrents_add, torrents_stats, compute_trending, update_status, get_trending
from mediastrends.tasks.database import sqlite_backup, backup_date, reset_database, reset_tables, load_sqlite_backup, create_database
from mediastrends.tasks.movies import get_trending as get_movies_trending, compute_trending as compute_movies_trending


#
# Logging
#

logger = logging.getLogger(__name__)


def setup_logging(verbose_level):
    verbose_to_level = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    if verbose_level > 0:
        verbose_level = 5 - (5 if verbose_level > 5 else verbose_level)
        dict_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                },
            },
            'handlers': {
                'default': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                },
            },
            'loggers': {
                'mediastrends': {
                    'handlers': ['default'],
                    'level': verbose_to_level[verbose_level],
                    'propagate': True
                }
            }
        }
        logging.config.dictConfig(dict_config)
    return


#
# Arguments definition
#

def _argument_config_file(parser):
    parser.add_argument("-f", "--config-dir", help="Configuration directory. Load mediastrends.MODE.ini", type=str)


def _argument_mode(parser):
    parser.add_argument("-m", "--mode", help="Mode. Override MEDIASTRENDS_MODE environment", type=str)


def _argument_verbose(parser):
    parser.add_argument("-v", "--verbose", help="Set mediastrend logger level, 0 to 5.", action="count", default=0)


def _argument_category(parser, **kwargs):
    parser.add_argument("-c", "--category", help="Torrents category", type=str, nargs='+', choices=["movies", "series", "unknown"], **kwargs)


def _argument_mindate(parser):
    parser.add_argument("-di", "--mindate", help="Min datetime: YYYYMMDDHHMM", type=lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M'))


def _argument_maxdate(parser):
    parser.add_argument("-dx", "--maxdate", help="Max datetime: YYYYMMDDHHMM", type=lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M'))


def _argument_tracker(parser):
    parser.add_argument("-t", "--tracker-name", help="Tracker name", type=str, choices=trackers_config.keys(), required=True)


def _argument_indexer(parser):
    parser.add_argument("-i", "--indexer", help="Indexer ID", type=str, choices=indexers_config.keys(), required=True)


def _arugment_tables(parser):
    parser.add_argument("-t", "--tables", help="Tables names", type=str, nargs='+', choices=["torrent", "torrenttracker", "tracker", "page", "stats", "trends", "imdb"], required=True)


def _argument_backup_date(parser):
    parser.add_argument("-d", "--backup-date", help="Backup date: YYYYMMDD-HHMM", type=backup_date)


def _argument_no_backup(parser):
    parser.add_argument("--no-backup", help="No backup are made", action='store_true')


def _argument_test(parser):
    parser.add_argument("--test", help="Action is not really called", action='store_true')


#
# abstract classes
#

# region
class AbstractParser(ABC):

    def __init__(self, parser=None):
        if parser is None:
            parser = argparse.ArgumentParser()
        self.parser = parser
        self.build()
        self.parsed_args_dict = {}
        self.parser.set_defaults(func=self.task)

    def build(self):
        return

    def task(self, **kwargs):
        raise NotImplementedError("This parser does not handle these arguments")

    def execute(self, args=sys.argv[1:]):
        parsed_args = self.parser.parse_args(args)
        self.parsed_args_dict = vars(parsed_args)

        parsed_args.func(**self.parsed_args_dict)


class AbstractSubParsers(ABC):

    def __init__(self, parent_parser, **kwargs):
        self.parent_parser = parent_parser
        self.subparsers = self.parent_parser.add_subparsers(**kwargs)
        self.add_parsers()

    @abstractmethod
    def add_parsers(self):
        return
# endregion

#
# Parsers
#

# region


class TorrentsTrendsGetParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_mindate(self.parser)
        _argument_maxdate(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        get_trending(**kwargs)


class TorrentsTrendsComputeParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_mindate(self.parser)
        _argument_maxdate(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        compute_trending(**kwargs)


class TorrentsAddParser(AbstractParser):

    def build(self):
        _argument_category(self.parser, required=True)
        _argument_indexer(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        torrents_add(**kwargs)


class TorrentsStatsParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_tracker(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        torrents_stats(**kwargs)


class TorrentsStatusParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        update_status(**kwargs)


class DatabaseResetTableParser(AbstractParser):

    def build(self):
        _argument_no_backup(self.parser)
        _arugment_tables(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        reset_tables(**kwargs)


class DatabaseResetDBParser(AbstractParser):

    def build(self):
        _argument_no_backup(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        reset_database(**kwargs)


class DatabaseBackupSaveParser(AbstractParser):

    def build(self):
        _argument_test(self.parser)

    def task(self, **kwargs):
        sqlite_backup(**kwargs)


class DatabaseBackupLoadParser(AbstractParser):

    def build(self):
        _argument_backup_date(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        load_sqlite_backup(**kwargs)


class DatabaseCreateParser(AbstractParser):

    def build(self):
        _argument_test(self.parser)

    def task(self, **kwargs):
        create_database(**kwargs)


class MoviesTrendsGetParser(AbstractParser):

    def build(self):
        _argument_mindate(self.parser)
        _argument_maxdate(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        get_movies_trending(**kwargs)


class MoviesTrendsComputeParser(AbstractParser):

    def build(self):
        _argument_mindate(self.parser)
        _argument_maxdate(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        compute_movies_trending(**kwargs)
# endregion

#
# MAIN PARSER (TOP LEVEL PARSER)
#

# region


class MediasTrendsCLI(AbstractParser):

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog='mediastrends',
            description="CLI to interact with mediastrends'tasks \n\n"
                        + "The logic steps to update database are:\n"
                        + "    1. torrents add\n"
                        + "    2. torrents stats\n"
                        + "    3. torrents trends compute\n"
                        + "    4. torrents status\n"
                        + "    5. torrents trends get",
            formatter_class=argparse.RawTextHelpFormatter
        )
        super().__init__(parser)

    def build(self):
        TopLevelSubParsers(self.parser, title="Top level commands")
        _argument_verbose(self.parser)
        _argument_config_file(self.parser)
        _argument_mode(self.parser)

    def execute(self, args=sys.argv[1:]):
        parsed_args = self.parser.parse_args(args)
        parsed_args_dict = vars(parsed_args)

        setup_logging(parsed_args_dict.get('verbose', 0))

        config_dir = parsed_args_dict.get('config_dir', None)
        mode = parsed_args_dict.get('mode', None)
        if config_dir or mode:
            cfg.populate_config(config=config, user_dir_config=config_dir, mode=mode, reload_=True)
            indexers_config.clear()
            indexers_config.update(cfg.read_indexers_file(config))
            trackers_config.clear()
            trackers_config.update(cfg.read_trackers_file(config))
            db_factory.defaut_instance = config.get('db', 'database')

        super().execute(args)

# endregion

#
# Sub Parsers
#

# region


class TopLevelSubParsers(AbstractSubParsers):

    def add_parsers(self):
        DatabaseSubParsers(self.subparsers.add_parser("database", help="Commands on database"), title="Database commands")
        TorrentsSubParsers(self.subparsers.add_parser("torrents", help="Commands on torrent"), title="Torrents commands")
        MoviesSubParsers(self.subparsers.add_parser("movies", help="Commands on movies"), title="Movies commands")


class DatabaseSubParsers(AbstractSubParsers):

    def add_parsers(self):
        DatabaseResetSubParsers(self.subparsers.add_parser("reset", help="reset actions on table/database"), title="Reset tables or database")
        DatabaseBackupSubParsers(self.subparsers.add_parser("backup", help="backups actions"), title="save or load backup")
        DatabaseCreateParser(self.subparsers.add_parser("create", help="Create database if not exist"))


class TorrentsSubParsers(AbstractSubParsers):

    def add_parsers(self):
        TorrentsAddParser(self.subparsers.add_parser("add", help="Add torrents in database"))
        TorrentsStatsParser(self.subparsers.add_parser("stats", help="Scrape and save seeders, leechers, completed from tracker"))
        TorrentsTrendsSubParsers(self.subparsers.add_parser("trends", help="Compute which torrents are most popular"))
        TorrentsStatusParser(self.subparsers.add_parser("status", help="Define which torrent are new, to follow and to forget"))


class MoviesSubParsers(AbstractSubParsers):

    def add_parsers(self):
        MoviesTrendsComputeParser(self.subparsers.add_parser("compute", help="Compute trending movies basend on movie torrents"))
        MoviesTrendsGetParser(self.subparsers.add_parser("get", help="Print trending movies basend on movie torrents"))


class TorrentsTrendsSubParsers(AbstractSubParsers):

    def add_parsers(self):
        TorrentsTrendsComputeParser(self.subparsers.add_parser("compute", help="Launch computation"))
        TorrentsTrendsGetParser(self.subparsers.add_parser("get", help="Print trending torrents"))


class DatabaseResetSubParsers(AbstractSubParsers):

    def add_parsers(self):
        DatabaseResetTableParser(self.subparsers.add_parser("table", help="drop and re-create table"))
        DatabaseResetDBParser(self.subparsers.add_parser("db", help="drop and re-create database"))


class DatabaseBackupSubParsers(AbstractSubParsers):

    def add_parsers(self):
        DatabaseBackupSaveParser(self.subparsers.add_parser("save", help="Create backup"))
        DatabaseBackupLoadParser(self.subparsers.add_parser("load", help="Load old backup into actual database"))
# endregion

#
# MAIN PROGRAM
#


def main():
    cli = MediasTrendsCLI()
    try:
        cli.execute()
    except NotImplementedError as err:
        logger.debug(err)
        cli.parser.print_help()


if __name__ == '__main__':
    main()
    exit()
