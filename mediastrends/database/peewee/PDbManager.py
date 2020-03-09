import peewee
from mediastrends import logger_app
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Page import Page
from mediastrends.stats.Stats import Stats
from ..DbManager import DbManager
from .PTorrent import PTorrent, PTorrentTracker
from .PTracker import PTracker
from .PPage import PPage
from .PStats import PStats


class PDbManager(DbManager):

    def __init__(self, config, db):
        self.db = db
        super().__init__(config)

    ##
    ## DB to object
    ##
    
    def db_to_torrent(db_torrent: PTorrent):
        torrent = Torrent(
            db_torrent.hash_info,
            db_torrent.name,
            db_torrent.pub_date,
            db_torrent.size
        )
        return torrent

    def db_to_tracker(db_tracker: PTracker):
        tracker = Tracker(
            db_tracker.scheme,
            db_tracker.netloc,
            db_tracker.path,
            db_tracker.name
        )
        return tracker

    def db_to_page(db_page):
        page = Page(
            url = db_page.url
        )
        return page

    ##
    ## TO DB (meaning get_or_create)
    ##

    def tracker_to_db(tracker: Tracker):
        db_tracker, created = PTracker.get_or_create(
            name = tracker.name,
            defaults = {'scheme': tracker.scheme, 'netloc': tracker.netloc, 'path': tracker.path}
        )
        if created:
            logger_app.info("Tracker has been created")

        return db_tracker

    def torrent_to_db(torrent: Torrent):        
        db_torrent, created = PTorrent.get_or_create(
            hash_info = torrent.hash_info,
            defaults = {'name': torrent.name, 'pub_date': torrent.pub_date, 'size': torrent.size}
        )
        if created:
            logger_app.info("Torrent has been created")

        return db_torrent


    ##
    ## Special save
    ##

    def save_page(page: Page, torrent: Torrent, tracker: Tracker):
        res = PDbManager.save_torrent_tracker(torrent, tracker)
        db_tracker = res.tracker
        db_torrent = res.torrent
    
        db_page, created = PPage.get_or_create(
            torrent = db_torrent,
            tracker = db_tracker,
            defaults = {'url': page.url}
        )

        if created:
            logger_app.info("Page has been created")

        return db_page

    def save_torrent_tracker(torrent: Torrent, tracker: Tracker):
        db_tracker = PDbManager.tracker_to_db(tracker)
        db_torrent = PDbManager.torrent_to_db(torrent)
        db_torrent_tracker, created = PTorrentTracker.get_or_create(tracker=db_tracker, torrent=db_torrent)
        if created:
            logger_app.info("Relation torrent-tracker has been created")

        return db_torrent_tracker
    
    def save_stats(stats: Stats):
        res = PDbManager.save_torrent_tracker(stats.torrent, stats.tracker)
        db_tracker = res.tracker
        db_torrent = res.torrent
        db_stats, created = PStats.get_or_create(
            tracker=db_tracker,
            torrent=db_torrent,
            valid_date=stats.valid_date,
            defaults = {
                'leechers': stats.leechers,
                'seeders': stats.seeders,
                'completed': stats.completed
            }
        )
        if created:
            logger_app.info("Stats for %s saved (%s)", stats.torrent.name, stats.valid_date)

        return db_stats

    ##
    ## GET DB BY ...
    ##

    def get_torrent_by_hash(hash_info: str):
        try:
            return PDbManager.db_to_torrent(PTorrent.get_or_none(hash_info = hash_info))
        except peewee.DoesNotExist:
            return None

    def get_tracker_by_name(name: str):
        return PDbManager.db_to_tracker(PTracker.get_or_none(name = name))