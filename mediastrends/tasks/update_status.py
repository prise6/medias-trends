import logging
from mediastrends import config, db_factory, logger_app, CATEGORY_NAME
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.TorrentsManager import TorrentsManager

logger = logging.getLogger(__name__)

def update_status(test, category: list = None, **kwargs):
    if test:
        logger.debug("get_trending task")
        return
    category = [CATEGORY_NAME.get(c) for c in category]
    torrents_manager = TorrentsManager(config, PDbManager, category)
    with db_factory.get_instance() as db:
        torrents_manager.update_torrents_status()

