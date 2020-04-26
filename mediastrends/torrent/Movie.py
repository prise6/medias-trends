from typing import List, Union
import logging
import imdb
from retry.api import retry_call
import mediastrends.tools.movies as tools_m
from mediastrends import config
from .Torrent import Torrent

logger = logging.getLogger(__name__)


class Movie:

    _RETRIES = config.getint('retry', 'tries')
    _DELAY = config.getint('retry', 'delay')

    def __init__(self, imdb_id: Union[int, str], torrents: List[Torrent] = None):
        self.torrents = torrents
        self.imdb_id = imdb_id
        self._imdb_resource = None
        self._imdb_access = None
        self._extras = {}

    @property
    def imdb_id(self):
        return self._imdb_id

    @imdb_id.setter
    def imdb_id(self, imdb_id: Union[int, str]):
        if isinstance(imdb_id, int):
            imdb_id = str(imdb_id)
        if not isinstance(imdb_id, str):
            raise TypeError("imdb_id must be instance of str (%s given)" % type(imdb_id))
        self._imdb_id = imdb_id

    @property
    def torrents(self):
        return self._torrents

    @torrents.setter
    def torrents(self, torrents=List[Torrent]):
        if torrents is None:
            return
        if not isinstance(torrents, list):
            raise TypeError("torrents must be instance of list (%s given)" % type(torrents))
        if not all([isinstance(t, Torrent) for t in torrents]):
            raise TypeError("torrents element must be instance of Torrent")
        if not all([Torrent._CAT_MOVIE == t.category for t in torrents]):
            raise ValueError("torrents element must have Torrent._CAT_MOVIE category")
        self._torrents = torrents

    @property
    def imdb_resource(self):
        if not self._imdb_resource:
            try:
                self.imdb_resource = retry_call(
                    tools_m.get_imdb_resource,
                    fkwargs={'type_': 'movie', 'id_': self.imdb_id, 'imdb_access': self.imdb_access},
                    tries=self._RETRIES,
                    delay=self._DELAY,
                    logger=logger,
                    exceptions=imdb.IMDbError
                )
            except Exception as err:
                raise ValueError('Couldn\'t retrieve imdb_resource with imdbpy (id: %s) - %s' % (self._imdb_id, err))
        return self._imdb_resource

    @imdb_resource.setter
    def imdb_resource(self, imdb_resource: imdb.Movie.Movie):
        if not isinstance(imdb_resource, imdb.Movie.Movie):
            raise TypeError('imdb_resource must be instance of imdb.Movie.Movie (%s given)' % (type(imdb_resource)))
        self._imdb_resource = imdb_resource

    @property
    def imdb_access(self):
        return self._imdb_access

    @imdb_access.setter
    def imdb_access(self, imdb_access):
        self._imdb_access = imdb_access

    def __getattr__(self, attr: str):
        if attr not in self._extras:
            if attr == 'cover_url':
                attr_imdb_data = 'cover url'
                attr_imdb_call = 'full-size cover url'
            else:
                attr_imdb_data = attr_imdb_call = attr.replace('_', ' ')
            if attr_imdb_data not in self.imdb_resource:
                # raise ValueError("Movie has no %s" % attr)
                return None
            self._extras[attr] = self.imdb_resource[attr_imdb_call]
        return self._extras.get(attr)

    def __str__(self):
        text = "          "
        text += self.title
        text += "\n"
        text += "Year:" + str(self.year)
        text += "\n"
        text += "id:" + self.imdb_id
        text += "\n"
        text += "Nombre de torrents:" + str(len(self.torrents))

        return text


#
# Class instanciation
#

def movies_from_title(title: str) -> List[Movie]:
    ia = tools_m.get_imdb_access()
    movies_results = ia.search_movie(title)
    movies_results = [m for m in movies_results if m.get('kind') == 'movie']
    movies = []
    for m in movies_results:
        movie = Movie(imdb_id=m.movieID)
        movie.imdb_access = ia
        movie._extras['year'] = m.get('year')
        movie._extras['title'] = m.get('title')
        movies.append(movie)

    return movies


def movies_from_group_torrents(groups: dict) -> List[Movie]:
    # movies dict with key = imdb_id
    movies = {}
    for title, infos in groups.items():
        selected_movie = None
        years = list(set([int(el.get('year', None)) for el in infos['parsed_names']]))
        try:
            titles_movies = movies_from_title(title)
            titles_movies = [m for m in titles_movies if m.year in years]
        except imdb.IMDbError:
            logger.warning("Couldn't search for movie: %s" % (title))
            continue
        if not titles_movies:
            # (trying another title from infos if needed)
            logger.warning("No movies found for title: %s" % (title))
            continue
        if len(titles_movies) >= 1:
            # suppose first one is the one
            # (see if year could be used if needed)
            selected_movie = titles_movies[0]

        if selected_movie.imdb_id in movies:
            same_movie = movies.get(selected_movie.imdb_id)
            same_movie.torrents = same_movie.torrents + infos['torrents']
        else:
            selected_movie.torrents = infos['torrents']
            movies[selected_movie.imdb_id] = selected_movie

    return [movie for movie in movies.values()]


def movies_from_torrents(torrents: List[Torrent]) -> List[Movie]:

    groups = tools_m.group_torrents_by_name(torrents)
    return movies_from_group_torrents(groups)
