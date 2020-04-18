import datetime
import logging
import peewee
from peewee import fn
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

logger = logging.getLogger(__name__)


class PDbManager(DbManager):

    #
    # Create DB
    #

    def create_database(db_connection):
        db_connection.create_tables([PTorrent, PTracker, PTorrentTracker, PPage, PStats, PTrends], safe=True)

    def drop_database(db_connection):
        db_connection.drop_tables([PTorrent, PTracker, PTorrentTracker, PPage, PStats, PTrends])

    #
    # DB to object
    #

    def db_to_torrent(db_torrent: PTorrent):
        torrent = Torrent(
            db_torrent.info_hash,
            db_torrent.name,
            db_torrent.pub_date,
            db_torrent.size,
            db_torrent.status,
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
            url=db_page.url
        )
        return page

    def db_to_stats(db_stats: PStats, torrent: Torrent = None, tracker: Tracker = None):
        stats = Stats(
            leechers=db_stats.leechers,
            seeders=db_stats.seeders,
            completed=db_stats.completed,
            tracker=tracker if tracker else PDbManager.db_to_tracker(db_stats.tracker),
            torrent=torrent if torrent else PDbManager.db_to_torrent(db_stats.torrent),
            valid_date=db_stats.valid_date
        )
        return stats

    #
    # TO DB (meaning get_or_create)
    #

    def tracker_to_db(tracker: Tracker, update=False):
        if not isinstance(tracker, Tracker):
            raise ValueError("Tracker must be Tracker instance")
        db_tracker, created = PTracker.get_or_create(
            name=tracker.name,
            defaults={'scheme': tracker.scheme, 'netloc': tracker.netloc, 'path': tracker.path}
        )
        updated = 0
        if created:
            logger.debug("Tracker has been created")
        else:
            try:
                assert db_tracker.scheme == tracker.scheme
                assert db_tracker.netloc == tracker.netloc
                assert db_tracker.path == tracker.path
            except AssertionError:
                db_tracker.scheme = tracker.scheme
                db_tracker.netloc = tracker.netloc
                db_tracker.path = tracker.path
                logger.debug("Tracker is different from database tracker")
                if update:
                    updated = db_tracker.save()
                    if updated > 0:
                        logger.debug("Tracker has been updated")
        return db_tracker, created, updated

    def torrent_to_db(torrent: Torrent, update=False):
        if not isinstance(torrent, Torrent):
            raise ValueError("torrent must be Torrent instance")
        db_torrent, created = PTorrent.get_or_create(
            info_hash=torrent.info_hash,
            defaults={'name': torrent.name, 'pub_date': torrent.pub_date, 'size': torrent.size, 'status': torrent.status, 'category': torrent.category}
        )
        updated = 0
        if created:
            logger.debug("Torrent has been created")
        else:
            try:
                # force torrent values
                assert db_torrent.name == torrent.name
                assert db_torrent.pub_date == torrent.pub_date
                assert db_torrent.size == torrent.size
                assert db_torrent.status == torrent.status
                assert db_torrent.category == torrent.category
            except AssertionError:
                db_torrent.name = torrent.name
                db_torrent.pub_date = torrent.pub_date
                db_torrent.size = torrent.size
                db_torrent.status = torrent.status
                db_torrent.category = torrent.category
                logger.debug("Torrent is different from database tracker")
                if update:
                    updated = db_torrent.save()
                    if updated > 0:
                        logger.debug("Torrent has been updated")

        return db_torrent, created, updated

    #
    # updates
    #

    def update(obj):
        class_name = obj.__class__.__name__.lower()
        method_to_call = "%s_to_db" % (class_name)
        try:
            method = getattr(PDbManager, method_to_call)
            db_obj, _, updated = method(obj, update=True)
        except AttributeError:
            raise ValueError("Method %s doesn't exist" % method_to_call)

        return db_obj, updated

    #
    # Special save
    #

    def save_page(page: Page, torrent: Torrent, tracker: Tracker):
        res, to_tr_c, to_c, tr_c = PDbManager.save_torrent_tracker(torrent, tracker)
        db_tracker = res.tracker
        db_torrent = res.torrent

        db_page, created = PPage.get_or_create(
            torrent=db_torrent,
            tracker=db_tracker,
            defaults={'url': page.url}
        )

        if created:
            logger.debug("Page has been created")

        return db_page, created

    def save_torrent_tracker(torrent: Torrent, tracker: Tracker):
        db_tracker, tracker_created, _ = PDbManager.tracker_to_db(tracker)
        db_torrent, torrent_created, _ = PDbManager.torrent_to_db(torrent)
        db_torrent_tracker, created = PTorrentTracker.get_or_create(tracker=db_tracker, torrent=db_torrent)
        if created:
            logger.debug("Relation torrent-tracker has been created")

        return db_torrent_tracker, created, torrent_created, tracker_created

    def save_stats(stats: Stats):
        res, _, _, _ = PDbManager.save_torrent_tracker(stats.torrent, stats.tracker)
        db_tracker = res.tracker
        db_torrent = res.torrent
        db_stats, created = PStats.get_or_create(
            tracker=db_tracker,
            torrent=db_torrent,
            valid_date=stats.valid_date,
            defaults={
                'leechers': stats.leechers,
                'seeders': stats.seeders,
                'completed': stats.completed
            }
        )
        if created:
            logger.debug("Stats for %s saved (%s)", stats.torrent.name, stats.valid_date)

        return db_stats, created

    def save_stats_collection_as_trends(stats_collection: StatsCollection):
        for torrent in stats_collection.torrents:
            db_torrent, _, _ = PDbManager.torrent_to_db(torrent)
            db_trends, created = PTrends.get_or_create(
                torrent=db_torrent,
                valid_date=stats_collection.valid_date,
                score=float(stats_collection.score)
            )
            if not created:
                logger.debug("Trends already saved")

    #
    # GET DB BY ...
    #

    def get_torrent_by_hash(info_hash: str):
        return PDbManager.db_to_torrent(PTorrent.get(info_hash=info_hash))

    def get_tracker_by_name(name: str):
        return PDbManager.db_to_tracker(PTracker.get(name=name))

    def get_stats_collection_by_torrent(torrent: Torrent):
        db_torrent, _, _ = PDbManager.torrent_to_db(torrent)
        stats_list = [PDbManager.db_to_stats(s, torrent) for s in db_torrent.stats]

        return StatsCollection(stats_list)

    def get_stats_collections_by_status(status: list, category: list = None, min_date=None, max_date=datetime.datetime.now()):

        torrents = PTorrent.select()

        if not isinstance(status, list):
            status = [status]
        predicate_torrents = PTorrent.status.in_(status)

        if category:
            if not isinstance(category, list):
                category = [category]
            predicate_torrents &= PTorrent.category.in_(category)

        torrents = torrents.where(predicate_torrents)

        stats = PStats.select(PStats, PTracker).join(torrents, on=(
            torrents.c.id == PStats.torrent_id
        )).switch(PStats).join(PTracker)

        if not min_date:
            min_date = max_date - datetime.timedelta(days=31)

        stats = stats.where(PStats.valid_date.between(min_date, max_date))

        torrents_with_stats = peewee.prefetch(torrents, stats)

        stats_collections = []
        for db_torrent in torrents_with_stats:
            torrent = PDbManager.db_to_torrent(db_torrent)
            stats_collections.append(StatsCollection([PDbManager.db_to_stats(s, torrent) for s in db_torrent.stats]))

        if len(stats_collections) == 0:
            raise ValueError("No stats collection with status '%s'" % status)

        return stats_collections

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

    def get_trending_torrents_by_category(category: list = None, min_date=None, max_date=None):

        if not min_date and not max_date:
            max_date = PDbManager.get_max_trend_date_by_category(category)
            if max_date is None:
                raise ValueError("Maximum trend date is null")
            min_date = max_date - datetime.timedelta(hours=1)

        sub_q = PTrends.select(PTrends.id, fn.row_number().over(
            partition_by=[PTrends.torrent],
            order_by=[PTrends.valid_date.desc()]
        ).alias("row_number")).where((PTrends.valid_date.between(min_date, max_date)))

        result = PTrends.select(PTrends, PTorrent).join(PTorrent)

        if category:
            if not isinstance(category, list):
                category = [category]
            result = result.where((PTorrent.category.in_(category)))

        result = result.join(sub_q, on=(
            (sub_q.c.row_number == 1)
            & (sub_q.c.id == PTrends.id)
        )).order_by(PTrends.score.desc())

        return [(PDbManager.db_to_torrent(db_trends.torrent), db_trends.score, db_trends.valid_date) for db_trends in result]

    #
    # SPECIAL REQUESTS
    #

    def get_max_trend_date_by_category(category: list = None):
        result = PTrends.select(fn.Max(PTrends.valid_date)).join(PTorrent)
        if category:
            if not isinstance(category, list):
                category = [category]
            result = result.where((PTorrent.category.in_(category)))
        return result.scalar()
