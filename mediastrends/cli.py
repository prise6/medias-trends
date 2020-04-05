import sys
import logging
from abc import ABC, abstractmethod
import argparse
import datetime
from mediastrends import config
import mediastrends.tasks as tasks
import mediastrends.tools.config as cfg

"""
mediastrends (CLI)
1. database --config-dir --mode
    1. reset
        1. table [tables ...] --no-safe/--safe
        2. db --safe/--no-safe
    2. backup
        1. save
        2. load --backup-date
2. torrents
    1. add --tracker --category
    2. stats --tracker --category
    3. trends
        1. compute --category --mindate --maxdate
        2. get --category --mindate --maxdate
    4. status --category
3. tests (do do)
"""
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
    parser.add_argument("-m", "--mode", help="Mode. Override MEDIATRENDS_MODE environment", type=str)


def _argument_verbose(parser):
    parser.add_argument("-v", "--verbose", help="Set mediastrend logger level, 0 to 5.", action="count", default=0)


def _argument_category(parser, **kwargs):
    parser.add_argument("-c", "--category", help="Torrents category", type=str, nargs='+', choices=["movies", "series", "unknown"], **kwargs)


def _argument_mindate(parser):
    parser.add_argument("-di", "--mindate", help="Min datetime: YYYYMMDDHHMM", type=lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M'))


def _argument_maxdate(parser):
    parser.add_argument("-dx", "--maxdate", help="Max datetime: YYYYMMDDHHMM", type=lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M'))


def _argument_tracker(parser):
    parser.add_argument("-t", "--tracker-name", help="Tracker name", type=str, choices=["ygg"], required=True)


def _arugment_tables(parser):
    parser.add_argument("-t", "--tables", help="Tables names", type=str, nargs='+', choices=["torrent", "torrenttracker", "tracker", "page", "stats", "trends"], required=True)


def _argument_backup_date(parser):
    parser.add_argument("-d", "--backup-date", help="Backup date: YYYYMMDD-HHMM", type=tasks.backup_date)


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
        tasks.get_trending(**kwargs)


class TorrentsTrendsComputeParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_mindate(self.parser)
        _argument_maxdate(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        tasks.compute_trending(**kwargs)


class TorrentsAddParser(AbstractParser):

    def build(self):
        _argument_category(self.parser, required=True)
        _argument_tracker(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        tasks.add_torrents(**kwargs)


class TorrentsStatsParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_tracker(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        tasks.get_stats(**kwargs)


class TorrentsStatusParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        tasks.update_status(**kwargs)


class DatabaseResetTableParser(AbstractParser):

    def build(self):
        _argument_no_backup(self.parser)
        _arugment_tables(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        tasks.reset_tables(**kwargs)


class DatabaseResetDBParser(AbstractParser):

    def build(self):
        _argument_no_backup(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        tasks.reset_database(**kwargs)


class DatabaseBackupSaveParser(AbstractParser):

    def build(self):
        _argument_test(self.parser)

    def task(self, **kwargs):
        tasks.sqlite_backup(**kwargs)


class DatabaseBackupLoadParser(AbstractParser):

    def build(self):
        _argument_backup_date(self.parser)
        _argument_test(self.parser)

    def task(self, **kwargs):
        tasks.load_sqlite_backup(**kwargs)

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

        super().execute(args)

# endregion

#
# Sub Parsers
#

# region


class TopLevelSubParsers(AbstractSubParsers):

    def add_parsers(self):
        DatabaseSubParsers(self.subparsers.add_parser("database", help="Commands on torrent"), title="Database commands")
        TorrentsSubParsers(self.subparsers.add_parser("torrents", help="Commands on database"), title="Torrents commands")


class DatabaseSubParsers(AbstractSubParsers):

    def add_parsers(self):
        DatabaseResetSubParsers(self.subparsers.add_parser("reset", help="reset actions on table/database"), title="Reset tables or database")
        DatabaseBackupSubParsers(self.subparsers.add_parser("backup", help="backups actions"), title="save or load backup")


class TorrentsSubParsers(AbstractSubParsers):

    def add_parsers(self):
        TorrentsAddParser(self.subparsers.add_parser("add", help="Add torrents in database"))
        TorrentsStatsParser(self.subparsers.add_parser("stats", help="Scrape and save seeders, leechers, completed from tracker"))
        TorrentsTrendsSubParsers(self.subparsers.add_parser("trends", help="Compute which torrents are most popular"))
        TorrentsStatusParser(self.subparsers.add_parser("status", help="Define which torrent are new, to follow and to forget"))


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
