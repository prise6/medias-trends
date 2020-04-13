import logging
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends import config, db_factory
from mediastrends.torznab.TorznabClient import TorznabJackettClient
from mediastrends.torznab.TorznabRSS import TorznabJackettRSS
from mediastrends.ygg.YggPage import YggPage
from mediastrends.torrent.Tracker import ygg_tracker, yts_tracker, Tracker

logger = logging.getLogger(__name__)


def add_torrents(test, indexer: str, category: list = None, **kwargs):
    if test:
        logger.debug("add_torrents task")
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

        _add_torrents_with_jackett(jackett_client, tracker)
    return


def _add_torrents_with_jackett(jackett_client: TorznabJackettClient, tracker: Tracker):
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
