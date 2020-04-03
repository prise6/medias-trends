import sys
from abc import ABC, abstractmethod, abstractstaticmethod
import argparse
import datetime
import mediastrends.tasks as tasks 

"""
mediastrends (CLI)
1. database
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

def _argument_category(parser):
    parser.add_argument("-c", "--category", help="Torrents category", type=str, nargs = '+', choices = ["movies", "series", "unknown"])

def _argument_mindate(parser):
    parser.add_argument("-di", "--mindate", help="Min datetime: YYYYMMDDHHMM", type=lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M'))

def _argument_maxdate(parser):
    parser.add_argument("-dx", "--maxdate", help="Max datetime: YYYYMMDDHHMM", type=lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M'))

def _argument_tracker(parser):
    parser.add_argument("-t", "--tracker-name", help="Tracker name", type=str, choices = ["ygg"])


class AbstractParser(ABC):

    def __init__(self, parser = argparse.ArgumentParser()):
        self.parser = parser
        self.build()
        self.parser.set_defaults(func=self.task)
    
    @abstractmethod
    def build():
        return

    def task():
        raise NotImplementedError()

    def execute(self, args = sys.argv[1:]):
        parsed_args = self.parser.parse_args(args)
        # print(vars(parsed_args))
        try:
            parsed_args.func(**vars(parsed_args))
        except Exception:
            self.parser.print_help()

class AbstractSubParsers(ABC):

    def __init__(self, parent_parser, **kwargs):
        self.parent_parser = parent_parser
        self.subparsers = self.parent_parser.add_subparsers(**kwargs)
        self.add_parsers()

    @abstractmethod
    def add_parsers(self):
        return


class TorrentsTrendsGetParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_mindate(self.parser)
        _argument_maxdate(self.parser)

    def task(self, **kwargs):
        tasks.get_trending(**kwargs)

class TorrentsTrendsComputeParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_mindate(self.parser)
        _argument_maxdate(self.parser)

    def task(self, **kwargs):
        print("compute_trending...")
        # tasks.compute_trending(**kwargs)

class TorrentsAddParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_tracker(self.parser)

    def task(self, **kwargs):
        print("add torrents...")
        # tasks.add_torrents(**kwargs)

class TorrentsStatsParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)
        _argument_tracker(self.parser)

    def task(self, **kwargs):
        print("stats torrents...")
        # tasks.get_stats(**kwargs)

class TorrentsStatusParser(AbstractParser):

    def build(self):
        _argument_category(self.parser)

    def task(self, **kwargs):
        print("Status torrents...")
        # tasks.get_stats(**kwargs)

class MediasTrendsCLI(AbstractParser):
    
    def build(self):
        TopLevelSubParsers(self.parser, title = "Top level commands")


class TopLevelSubParsers(AbstractSubParsers):

    def add_parsers(self):
        DatabaseSubParsers(self.subparsers.add_parser("database", help = "Commands on torrent"), title = "Database commands")
        TorrentsSubParsers(self.subparsers.add_parser("torrents", help = "Command on database"), title = "Torrents commands")


class DatabaseSubParsers(AbstractSubParsers):

    def add_parsers(self):
        self.subparsers.add_parser("reset", help = "reset actions on table/database")
        self.subparsers.add_parser("backup", help = "backups actions")

class TorrentsSubParsers(AbstractSubParsers):

    def add_parsers(self):
        TorrentsAddParser(self.subparsers.add_parser("add", help = "Add torrents in database"))
        TorrentsStatsParser(self.subparsers.add_parser("stats", help = "Scrape and save seeders, leechers, completed from tracker"))
        TorrentsTrendsSubParsers(self.subparsers.add_parser("trends", help = "Compute which torrents are most popular"))
        TorrentsStatusParser(self.subparsers.add_parser("status", help = "Define which torrent are new, to follow and to forget"))

class TorrentsTrendsSubParsers(AbstractSubParsers):

    def add_parsers(self):
        TorrentsTrendsComputeParser(self.subparsers.add_parser("compute", help = "Launch computation"))
        TorrentsTrendsGetParser(self.subparsers.add_parser("get", help = "Print trending torrents"))
        





if __name__ == '__main__':
    cli = MediasTrendsCLI()
    cli.execute()
