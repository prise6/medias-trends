import datetime
import logging
from mediastrends import config, db_factory, indexers_config, CATEGORY_NAME, trackers_config
from mediastrends.database.peewee.PDbManager import PDbManager

from mediastrends.torznab.TorznabClient import TorznabJackettClient
from mediastrends.torznab.TorznabRSS import TorznabJackettRSS, TorznabJackettResult

from mediastrends.torrent.Tracker import Tracker, tracker_from_config_by_name, tracker_from_config_by_url
from mediastrends.torrent.Page import Page
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.TorrentsManager import TorrentsManager

from mediastrends.trends.TrendsManager import TrendsManager
from mediastrends.trends.TrendsEngine import NormalizedTrendsEngine

import mediastrends.stats as stats


logger = logging.getLogger(__name__)


# region
def torrents_add(test, indexer: str, category: list = None, **kwargs):
    nb_torrent = 0
    if test:
        logger.debug("torrents_add task")
        return nb_torrent

    assert category is not None
    assert indexer in indexers_config

    for cat in category:
        logger.debug("Category: %s" % cat)
        logger.debug("Indexer: %s" % indexer)
        if cat not in ['movies', 'series']:
            logger.error("category must be movies or series " % cat)
            break
        try:
            client = create_torznab_from_cli_params(indexer, cat)
        except Exception as err:
            logger.error("Error during jacket creation: %s" % str(err))
            break

        try:
            rss_content = client.get_rss_content()
            rss_parser = TorznabJackettRSS(rss_content)
            rss_parser.process_items()
        except Exception as err:
            logger.error("Error while contacting jackett: %s" % str(err))

        if len(rss_parser.items) == 0:
            logger.warning('RSS feed is empty')
            break

        db = db_factory.get_instance()
        for item in rss_parser.items:
            try:
                torznab_result = elements_from_torznab_result(item)
                if not torznab_result['keep']:
                    pass

                with db:
                    for tracker in torznab_result['trackers']:
                        _, _, to_created, _ = PDbManager.save_torrent_tracker(
                            torrent=torznab_result['torrent'],
                            tracker=tracker
                        )

                        nb_torrent += to_created
            except Exception as err:
                logger.error("Error during elements creation: %s" % str(err))
                pass

    logger.debug("%s torrents added" % nb_torrent)

    return nb_torrent


def create_torznab_from_cli_params(indexer: str, category: str):
    client = TorznabJackettClient(config)
    client.indexer = indexer
    indexer = indexers_config.get(indexer).get(category)
    if not indexer:
        raise Exception("Indexer %s with category %s doesn't exist" % (indexer, category))
    if not indexer.get('active', False):
        raise Exception("Indexer %s with category %s is not active" % (indexer, category))
    if 'action' not in indexer:
        raise Exception("Action param must be set")
    client.action = indexer.get('action')
    if isinstance(indexer.get('params', None), dict):
        for param, value in indexer.get('params').items():
            client.add_param(param, value)
    return client


def elements_from_torznab_result(result: TorznabJackettResult) -> dict:
    elements = dict.fromkeys(['keep', 'page', 'torrent', 'trackers'], None)
    elements['keep'] = False
    elements['trackers'] = []
    elements['torrent'] = result.to_torrent_file()
    elements['page'] = Page(result.get('guid'))
    if elements.get('torrent').tracker_urls is None:
        return elements
    for tracker_url in elements.get('torrent').tracker_urls:
        tracker = tracker_from_config_by_url(tracker_url)
        if tracker is not None:
            elements['trackers'].append(tracker)
            elements['keep'] = True
    return elements
# endregion


# region
def torrents_stats(test, tracker_name: str, category: list = None, **kwargs):
    nb_stats = 0
    if test:
        logger.debug("torrents_stats task")
        return nb_stats

    assert tracker_name in trackers_config
    assert isinstance(category, list)

    logger.debug("Tracker: %s" % tracker_name)
    logger.debug("Category: %s" % ', '.join(category))

    if not trackers_config.get(tracker_name).get('active', False):
        return nb_stats

    tracker = tracker_from_config_by_name(tracker_name)

    if category is not None:
        category = [CATEGORY_NAME[c] for c in category]

    nb_stats = torrents_stats_with_tracker(tracker, category)

    return nb_stats


def torrents_stats_with_tracker(tracker: Tracker, category: list = None):
    nb_stats = 0
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
            _, created = PDbManager.save_stats(tracker_stats)
            nb_stats += created

    return nb_stats
# endregion


# region
def compute_trending(test, category: list = None, mindate=None, maxdate=datetime.datetime.now(), **kwargs):
    if category is not None:
        category = [CATEGORY_NAME.get(c) for c in category]
    if test:
        logger.debug("compute_trending task")
        return
    with db_factory.get_instance():
        trends_manager = TrendsManager(config, PDbManager, category, mindate, maxdate)
        trends_manager.evaluate(NormalizedTrendsEngine())
        trends_manager.save_trends()
# endregion


# region
def update_status(test, category: list = None, **kwargs):
    if test:
        logger.debug("get_trending task")
        return
    if category is not None:
        category = [CATEGORY_NAME.get(c) for c in category]
    torrents_manager = TorrentsManager(config, PDbManager, category)
    with db_factory.get_instance():
        torrents_manager.update_torrents_status()
    return
# endregion


# region
def get_trending(test, category: list = None, mindate=None, maxdate=None, **kwargs):

    if category is not None:
        category = [CATEGORY_NAME.get(c) for c in category]

    results = None

    if test:
        logger.debug("get_trending task")
        return
    try:
        with db_factory.get_instance():
            results = PDbManager.get_trending_torrents_by_category(category, mindate, maxdate)

        for t, score, valid_date in results:
            print("%s / %s / %s" % (t, score, valid_date))
    except ValueError as err:
        logger.warning(err)
    return results
# endregion
