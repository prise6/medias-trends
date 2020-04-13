import logging
from mediastrends import db_factory, CATEGORY_NAME
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker, ygg_tracker, yts_tracker
import mediastrends.stats as stats

logger = logging.getLogger(__name__)


def get_stats(test, tracker_name, category, **kwargs):
    if test:
        logger.debug("get_stats task")
        return
    tracker = None
    if category is not None:
        category = [CATEGORY_NAME.get(c) for c in category]
    if tracker_name == 'ygg':
        tracker = ygg_tracker
    if tracker_name == 'yts':
        tracker = yts_tracker
    _get_stats_with_tracker(tracker, category)
    return


def _get_stats_with_tracker(tracker: Tracker, category: list = None):

    with db_factory.get_instance():
        torrents = PDbManager.get_torrents_by_tracker(tracker, status=[Torrent._STATUS_NEW, Torrent._STATUS_FOLLOW], category=category)
        logger.debug("Torrents number: %s", len(torrents))

        stats_scraper = stats.StatsScraper(tracker)
        stats_scraper.torrents = torrents
        stats_scraper.run_by_batch()

        stats_collection = stats_scraper.stats_collection
        logger.debug("Stats number: %s", stats_collection.count())

        if stats_collection.count() != len(torrents):
            logger.warning("Statistics count is wrong %s/%s", stats_collection.count(), len(torrents))

    with db_factory.get_instance():
        for tracker_stats in stats_collection.stats:
            PDbManager.save_stats(tracker_stats)

    return
