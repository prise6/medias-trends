import logging
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends import config, db_factory, CATEGORY_NAME
import mediastrends.ygg as ygg

logger = logging.getLogger(__name__)


def add_torrents(test, tracker_name: str, category: list = None, **kwargs):
    if test:
        logger.debug("add_torrents task")
        return

    assert category is not None

    for c in category:
        if tracker_name == 'ygg':
            _add_ygg_torrents(c)

    return


def _add_ygg_torrents(category: str):

    assert category in CATEGORY_NAME.keys()

    rss_file = "rss_%s" % category

    ygg_rss = ygg.rss_from_feedparser(config.get('ygg', rss_file))
    _N_ITEMS = len(ygg_rss.items)

    if _N_ITEMS == 0:
        logger.warning("RSS feed is empty")
    db_page = None
    db = db_factory.get_instance()
    with db:
        for idx, item in enumerate(ygg_rss.items):
            logger.debug("---> RSS item %s/%s ... " % (idx + 1, _N_ITEMS))
            ygg_page = ygg.page_from_rss_item(ygg_rss, idx, True)
            ygg_torrent = ygg.torrent_from_page(ygg_page)

            db_page = PDbManager.save_page(ygg_page, ygg_torrent, ygg.tracker)
    return db_page
