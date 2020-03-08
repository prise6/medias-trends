from mediastrends import logger_app
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker
from ..DbManager import DbManager
from .PTorrent import PTorrent
from .PTracker import PTracker


class PDbManager(DbManager):

    def __init__(self, config, db):
        self.db = db
        super().__init__(config)
    
    def db_to_torrent(db_torrent: PTorrent):
        torrent = Torrent(
            db_torrent.hash_info,
            db_torrent.name,
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
            pub_date = torrent.pub_date
        )
        return db_torrent

    def save_torrent(torrent: Torrent):
        db_torrent = PDbManager.torrent_to_db(torrent)
        return db_torrent.save()

    def save_tracker(tracker: Tracker):
        db_tracker = PDbManager.tracker_to_db(tracker)
        return db_tracker.save()

    def get_torrent_by_hash(hash_info: str):
        return

    def get_tracker_by_name(name: str):
        return