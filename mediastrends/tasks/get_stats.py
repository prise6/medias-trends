import logging
from mediastrends import db_factory, CATEGORY_NAME
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.Torrent import Torrent
import mediastrends.stats as stats
import mediastrends.ygg as ygg

logger = logging.getLogger(__name__)


def get_stats(test, tracker_name, category, **kwargs):
    if test:
        logger.debug("get_stats task")
        return
    if category is not None:
        category = [CATEGORY_NAME.get(c) for c in category]
    if tracker_name == 'ygg':
        _get_ygg_stats(category)
    return


def _get_ygg_stats(category: list = None):
    with db_factory.get_instance():
        torrents = PDbManager.get_torrents_by_tracker(ygg.tracker, status=[Torrent._STATUS_NEW, Torrent._STATUS_FOLLOW], category=category)
        logger.debug("Torrents number: %s", len(torrents))

        stats_scraper = stats.StatsScraper(ygg.tracker)
        stats_scraper.torrents = torrents
        stats_scraper.run_by_batch()

        stats_collection = stats_scraper.stats_collection
        logger.debug("Stats number: %s", stats_collection.count())

        if stats_collection.count() != len(torrents):
            logger.warning("Statistics count is wrong %s/%s", stats_collection.count(), len(torrents))

    with db_factory.get_instance():
        for ygg_stats in stats_collection.stats:
            db_stats = PDbManager.save_stats(ygg_stats)
    return db_stats
