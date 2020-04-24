import logging
from mediastrends import db_factory
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.Movie import movies_from_torrents
from mediastrends.torrent.Torrent import Torrent

logger = logging.getLogger(__name__)


# region
def get_trending(test, mindate=None, maxdate=None, **kwargs):
    if test:
        logger.debug("get_trending task")
        return
    with db_factory.get_instance():
        trendings_torrents = PDbManager.get_trending_torrents_by_category(Torrent._CAT_MOVIE, mindate, maxdate)

    trendings_movies = movies_from_torrents([t for t, _, _ in trendings_torrents])

    for movie in trendings_movies:
        print(movie)
        print("------------")
# endregion
