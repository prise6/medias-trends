import peewee
from mediastrends import logger_app
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Page import Page
from ..DbManager import DbManager
from .PTorrent import PTorrent
from .PTracker import PTracker
from .PPage import PPage


class PDbManager(DbManager):

    def __init__(self, config, db):
        self.db = db
        super().__init__(config)
    
    def db_to_torrent(db_torrent: PTorrent):
        torrent = Torrent(
            db_torrent.hash_info,
            db_torrent.name,
            db_torrent.pub_date,
            db_torrent.size,
            PDbManager.db_to_tracker(db_torrent.tracker)
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

    def tracker_to_db(tracker: Tracker):
        db_tracker = PTracker(
            name = tracker.name,
            scheme = tracker.scheme,
            netloc = tracker.netloc,
            path = tracker.path
        )
        return db_tracker

    def torrent_to_db(torrent: Torrent):
        db_tracker, create = PTracker.get_or_create(
            name = torrent.tracker.name,
            scheme = torrent.tracker.scheme,
            netloc = torrent.tracker.netloc,
            path = torrent.tracker.path
        )
        if create:
            logger_app.info("Tracker has been created")
        db_torrent = PTorrent(
            hash_info = torrent.hash_info,
            tracker = db_tracker,
            name = torrent.name,
            pub_date = torrent.pub_date,
            size = torrent.size
        )
        return db_torrent

    def page_to_db(page: Page, torrent: Torrent):
        db_torrent = PDbManager.torrent_to_db(torrent)
        
        db_page = PPage(
            torrent = db_torrent,
            url = page.url
        )
        return db_page

    def save_torrent(torrent: Torrent, update=True, force=True):
        db_torrent = PDbManager.torrent_to_db(torrent)
        try: 
            logger_app.info("Trying saving torrent...")
            res = db_torrent.save(force_insert=force)
        except peewee.IntegrityError as err:
            if update:
                logger_app.info("Updating torrent...")
                res = db_torrent.save(force_insert=False)
            else:
                logger_app.info("No action...")
                res = 0
        logger_app.info("Done.")
        return res


    def save_tracker(tracker: Tracker):
        db_tracker = PDbManager.tracker_to_db(tracker)
        return db_tracker.save()

    def save_page(page: Page, torrent: Torrent):
        db_page = PDbManager.page_to_db(page, torrent)
        db_page_id = PPage.replace(torrent = db_page.torrent, url = db_page.url).execute()
        return db_page_id

    def get_torrent_by_hash(hash_info: str):
        try:
            return PDbManager.db_to_torrent(PTorrent.get_by_id(hash_info))
        except peewee.DoesNotExist:
            return None

    def get_tracker_by_name(name: str):
        return PDbManager.db_to_tracker(PTracker.get_or_none(name = name))