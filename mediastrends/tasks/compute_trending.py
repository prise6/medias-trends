import datetime
import logging
from mediastrends import config, db_factory, CATEGORY_NAME
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.trends.TrendsManager import TrendsManager
from mediastrends.trends.TrendsEngine import ClassicTrendsEngine

logger = logging.getLogger(__name__)


def compute_trending(test, category: list = None, mindate=None, maxdate=datetime.datetime.now(), **kwargs):
    if category is not None:
        category = [CATEGORY_NAME.get(c) for c in category]
    if test:
        logger.debug("compute_trending task")
        return
    with db_factory.get_instance():
        trends_manager = TrendsManager(config, PDbManager, category, mindate, maxdate)
        trends_manager.evaluate(ClassicTrendsEngine())
        trends_manager.save_trends()
