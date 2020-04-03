import datetime
import logging
from mediastrends import config, db_factory, logger_app, CATEGORY_NAME
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.trends.TrendsManager import TrendsManager
from mediastrends.trends.TrendsEngine import ClassicTrendsEngine
from mediastrends.torrent.Torrent import Torrent

logger = logging.getLogger(__name__)

def compute_trending(test, category: list = None, mindate = None, maxdate = datetime.datetime.now(), **kwargs):
    category = [CATEGORY_NAME.get(c) for c in category]
    if test:
        logger.debug("compute_trending task")
        return
    try:
        with db_factory.get_instance() as db:
            trends_manager = TrendsManager(config, PDbManager, category, mindate, maxdate)
            trends_manager.evaluate(ClassicTrendsEngine())
            trends_manager.save_trends()
    except ValueError as err:
        logger_app.info("No torrent in category %s", category)

