import logging
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends import config, db_factory, indexers_config
from mediastrends.torznab.TorznabClient import TorznabJackettClient
from mediastrends.torznab.TorznabRSS import TorznabJackettRSS, TorznabJackettResult
from mediastrends.torrent.Tracker import tracker_from_config_by_url
from mediastrends.torrent.Page import Page

logger = logging.getLogger(__name__)


def torrents_add(test, indexer: str, category: list = None, **kwargs):
    nb_torrent = 0
    if test:
        logger.debug("torrents_add task")
        return nb_torrent

    assert category is not None
    assert indexer in indexers_config

    for cat in category:
        logger.debug("Category: %s" % cat)
        if cat not in ['movies', 'series']:
            logger.error("category must be movies or series " % cat)
            break
        try:
            client = create_torznab_from_cli_params(indexer, cat)
        except Exception as err:
            logger.error("Error during jacket creation: %s" % str(err))
            break

        rss_content = client.get_rss_content()
        rss_parser = TorznabJackettRSS(rss_content).process_items()
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
                    _, create = PDbManager.save_page(
                        page=torznab_result['page'],
                        torrent=torznab_result['torrent'],
                        tracker=torznab_result['tracker']
                    )
                    nb_torrent += create
            except Exception as err:
                logger.error("Error during elements creation: %s" % str(err))
                pass

    logger.debug("%s torrents added" % nb_torrent)

    return nb_torrent


def create_torznab_from_cli_params(indexer: str, category: str):
    client = TorznabJackettClient(config)
    client.indexer = indexer
    indexer = indexers_config.get(indexer).get(category)
    if not indexer.get('active'):
        raise Exception("Indexer %s with category %s is not active" % (indexer, category))
    if 'action' not in indexer:
        raise Exception("Action param must be set")
    client.action = indexer.get('action')
    if isinstance(indexer.get('params', None), dict):
        for param, value in indexer.get('params').items():
            client.add_param(param, value)
    return client


def elements_from_torznab_result(result: TorznabJackettResult) -> dict:
    elements = dict.fromkeys(['keep', 'page', 'torrent', 'tracker'], None)
    elements['keep'] = False
    elements['torrent'] = result.to_torrent_file()
    elements['page'] = Page(result.get('guid'))
    if elements.get('torrent').tracker_urls is None:
        return elements
    for tracker_url in elements.get('torrent').tracker_urls:
        tracker = tracker_from_config_by_url(tracker_url)
        if tracker is not None:
            elements['tracker'] = tracker
            elements['keep'] = True
            break

    return elements
