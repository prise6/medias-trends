import logging
from mediastrends import db_factory
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.IMDBObject import movies_from_torrents
from mediastrends.torrent.Torrent import Torrent

logger = logging.getLogger(__name__)


# region
def compute_trending(test, mindate=None, maxdate=None, **kwargs):
    if test:
        logger.debug("get_trending task")
        return
    with db_factory.get_instance():
        trendings_torrents = PDbManager.get_trending_torrents_by_category(Torrent._CAT_MOVIE, mindate, maxdate)

    trendings_movies = movies_from_torrents([t for t, _, _ in trendings_torrents])

    with db_factory.get_instance():
        for movie in trendings_movies:
            try:
                PDbManager.imdb_object_to_db(movie)
            except Exception as err:
                logger.error('Error during imdb object creation (%s): %s' % (movie.imdb_id, err))
# endregion


# region
def get_trending(test, mindate=None, maxdate=None, **kwargs):
    if test:
        logger.debug("get_trending task")
        return
    with db_factory.get_instance():
        results = PDbManager.get_trending_movies()
        for item in results:
            print(item)

    return results
# endregion
