import logging
from mediastrends import db_factory, CATEGORY_NAME
from mediastrends.database.peewee.PDbManager import PDbManager

logger = logging.getLogger(__name__)


def get_trending(test, category: list = None, mindate=None, maxdate=None, **kwargs):

    if category is not None:
        category = [CATEGORY_NAME.get(c) for c in category]

    if test:
        logger.debug("get_trending task")
        return
    try:
        with db_factory.get_instance():
            result = PDbManager.get_trending_torrents_by_category(category, mindate, maxdate)

        for t, score, valid_date in result:
            print("%s / %s / %s" % (t, score, valid_date))
    except ValueError as err:
        logger.warning(err)
    return result
