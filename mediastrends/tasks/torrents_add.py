import logging
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends import config, db_factory, indexers_config
from mediastrends.torznab.TorznabClient import TorznabJackettClient
from mediastrends.torznab.TorznabRSS import TorznabJackettRSS, TorznabJackettResult
from mediastrends.torrent.Tracker import ygg_tracker, yts_tracker, Tracker, tracker_from_config_by_url
from mediastrends.torrent.Page import Page
from mediastrends.ygg.YggPage import YggPage

logger = logging.getLogger(__name__)


def torrents_add(test, indexer: str, category: list = None, **kwargs):
    if test:
        logger.debug("torrents_add task")
        return

    assert category is not None

    jackett_client = TorznabJackettClient(config)
    tracker = None
    for c in category:
        if indexer == 'yggtorrent':
            jackett_client.indexer = 'yggtorrent'
            jackett_client.action = 'search'
            tracker = ygg_tracker
            if c == "movies":
                jackett_client.add_param('cat', 102183)
            if c == "series":
                jackett_client.add_param('cat', 102185)
        if indexer == 'yts':
            jackett_client.indexer = 'yts'
            tracker = yts_tracker
            jackett_client.action = 'search'
            if c == "movies":
                jackett_client.add_param('cat', 2000)

        _torrents_add_with_jackett(jackett_client, tracker)
    return


def create_torznab_from_cli_params(indexer: str, category: str):
    client = TorznabJackettClient(config)
    indexer = indexers_config.get(indexer).get(category)
    if 'action' not in indexer:
        raise Exception("action params must be set")
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


def _torrents_add_with_jackett(jackett_client: TorznabJackettClient, tracker: Tracker):
    rss_content = jackett_client.get_rss_content()
    rss_parser = TorznabJackettRSS(rss_content)
    rss_parser.process_items()

    _N_ITEMS = len(rss_parser.items)

    if _N_ITEMS == 0:
        logger.warning("RSS feed is empty")
    db = db_factory.get_instance()
    with db:
        for idx, el in enumerate(rss_parser.items):
            logger.debug("---> Torznab element %s/%s ... " % (idx + 1, _N_ITEMS))
            page = YggPage(el.get('guid'))
            torrent_file = el.to_torrent_file()
            PDbManager.save_page(page, torrent_file, tracker)
    return
