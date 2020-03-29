import peewee
from mediastrends import logger_app
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker
from mediastrends.torrent.Page import Page
from mediastrends.stats import Stats
from mediastrends.stats import StatsCollection
from ..DbManager import DbManager
from .PTorrent import PTorrent, PTorrentTracker
from .PTracker import PTracker
from .PPage import PPage
from .PStats import PStats
from .PTrends import PTrends


class PDbManager(DbManager):

    def __init__(self, config, db):
        self.db = db
        super().__init__(config)

    ##
    ## DB to object
    ##
    
    def db_to_torrent(db_torrent: PTorrent):
        torrent = Torrent(
            db_torrent.info_hash,
            db_torrent.name,
            db_torrent.pub_date,
            db_torrent.size,
            db_torrent.category,
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

    def db_to_page(db_page: PPage):
        page = Page(
            url = db_page.url
        )
        return page

    def db_to_stats(db_stats: PStats, torrent: Torrent = None, tracker: Tracker = None):
        stats = Stats(
            leechers = db_stats.leechers,
            seeders = db_stats.seeders,
            completed = db_stats.completed,
            tracker = tracker if tracker else PDbManager.db_to_tracker(db_stats.tracker),
            torrent = torrent if torrent else PDbManager.db_to_torrent(db_stats.torrent),
            valid_date = db_stats.valid_date
        )
        return stats

    ##
    ## TO DB (meaning get_or_create)
    ##

    def tracker_to_db(tracker: Tracker):
        if not isinstance(tracker, Tracker):
            raise ValueError("Tracker must be Tracker instance")
        db_tracker, created = PTracker.get_or_create(
            name = tracker.name,
            defaults = {'scheme': tracker.scheme, 'netloc': tracker.netloc, 'path': tracker.path}
        )
        if created:
            logger_app.info("Tracker has been created")
        else:
            db_tracker.scheme = tracker.scheme
            db_tracker.netloc = tracker.netloc
            db_tracker.path = tracker.path

        return db_tracker

    def torrent_to_db(torrent: Torrent):
        if not isinstance(torrent, Torrent):
            raise ValueError("torrent must be Torrent instance")
        db_torrent, created = PTorrent.get_or_create(
            info_hash = torrent.info_hash,
            defaults = {'name': torrent.name, 'pub_date': torrent.pub_date, 'size': torrent.size, 'status': torrent.status, 'category': torrent.category}
        )
        if created:
            logger_app.info("Torrent has been created")
        else:
            #force torrent values
            db_torrent.name = torrent.name
            db_torrent.pub_date = torrent.pub_date
            db_torrent.size = torrent.size
            db_torrent.status = torrent.status
            db_torrent.category = torrent.category

        return db_torrent

    ##
    ## updates
    ##

    def update(obj):
        class_name = obj.__class__.__name__.lower()
        method_to_call = "%s_to_db" % (class_name)
        try:
            method = getattr(PDbManager, method_to_call)
            db_obj = method(obj)
        except AttributeError as err:
            raise ValueError("Method %s doesn't exist" % method_to_call)
        
        return db_obj, db_obj.save()


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

    def save_stats_collection_as_trends(stats_collection: StatsCollection):
        for torrent in stats_collection.torrents:
            db_torrent = PDbManager.torrent_to_db(torrent)
            PTrends.create(
                torrent = db_torrent,
                valid_date = stats_collection.valid_date,
                score = float(stats_collection.score)
            )


    ##
    ## GET DB BY ...
    ##

    def get_torrent_by_hash(info_hash: str):
        return PDbManager.db_to_torrent(PTorrent.get(info_hash = info_hash))

    def get_tracker_by_name(name: str):
        return PDbManager.db_to_tracker(PTracker.get(name = name))

    def get_stats_collection_by_torrent(torrent: Torrent):
        db_torrent = PDbManager.torrent_to_db(torrent)
        stats_list = [PDbManager.db_to_stats(s, torrent) for s in db_torrent.stats]

        return StatsCollection(stats_list)
    
    def get_torrents_by_status(status: list, category: list = None):
        result = PTorrent.select()
        
        if not isinstance(status, list):
            status = [status]

        expression = PTorrent.status.in_(status)
        
        if category:
            if not isinstance(category, list):
                category = [category]
            expression &= PTorrent.category.in_(category)

        result = result.where(expression)

        if result.count() == 0:
            raise ValueError("No torrent with status '%s'" % status)
        
        return [PDbManager.db_to_torrent(db_torrent) for db_torrent in result]

    def get_torrents_by_tracker(tracker: Tracker, status: list = None, category: list = None):
        result = PTorrent.select().join(PTorrentTracker).join(PTracker)
        expression = (PTracker.name == tracker.name)
        if status:
            if not isinstance(status, list):
                status = [status]
            expression &= (PTorrent.status.in_(status))
        if category:
            if not isinstance(category, list):
                category = [category]
            expression &= (PTorrent.category.in_(category))

        result = result.where(expression)
        return [PDbManager.db_to_torrent(db_torrent) for db_torrent in result]

