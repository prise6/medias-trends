import datetime
import logging
from mediastrends import config, db_factory, logger_app, CATEGORY_NAME
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.Torrent import Torrent

logger = logging.getLogger(__name__)

def get_trending(test, category: list = None, mindate = None, maxdate = None, **kwargs):
    category = [CATEGORY_NAME.get(c) for c in category]
    if test:
        logger.debug("get_trending task")
        return
    with db_factory.get_instance() as db:
        result = PDbManager.get_trending_torrents_by_category(category, mindate, maxdate)

    for t, score, valid_date in result:
        print("%s / %s / %s" % (t, score, valid_date))

