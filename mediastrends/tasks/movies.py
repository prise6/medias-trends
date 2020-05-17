import logging
from mediastrends import db_factory, config, CATEGORY_NAME
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.IMDBObject import movies_from_torrents
from mediastrends.torrent.TorrentsManager import TorrentsManager

logger = logging.getLogger(__name__)


# region
def compute_trending(test, **kwargs):
    if test:
        logger.debug("get_trending task")
        return

    trendings_movies = []

    torrents_manager = TorrentsManager(config, PDbManager, CATEGORY_NAME['movies'])

    try:
        with db_factory.get_instance():
            # trendings_torrents = PDbManager.get_trending_torrents_by_category(Torrent._CAT_MOVIE, mindate, maxdate, delta_hours)
            trendings_torrents = torrents_manager.torrents_trending
        trendings_movies = movies_from_torrents([t for t, _, _ in trendings_torrents])
    except ValueError as err:
        logger.warning(err)
        return

    with db_factory.get_instance():
        for movie in trendings_movies:
            try:
                PDbManager.imdb_object_to_db(movie, update=True)
            except Exception as err:
                logger.error('Error during imdb object creation (%s): %s' % (movie.imdb_id, err))
# endregion


# region
def get_trending(test, mindate=None, maxdate=None, delta_hours=1, **kwargs):

    results = None

    if test:
        logger.debug("get_trending task")
        return
    try:
        with db_factory.get_instance():
            results = PDbManager.get_trending_movies(mindate, maxdate, delta_hours)
            for item in results:
                print(item)
    except ValueError as err:
        logger.warning(err)
    return results
# endregion
