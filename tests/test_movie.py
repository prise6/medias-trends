import unittest
import random
from unittest.mock import patch
import datetime
import imdb
import mediastrends.tools.movies as tools_m
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Movie import Movie
from mediastrends.torrent.Movie import movies_from_group_torrents, movies_from_title


def generate_torrents(nb):
    return [Torrent(
        info_hash='%40x' % random.getrandbits(160),
        name="name",
        size=random.randint(200, 5000),
        pub_date=datetime.datetime.now(),
        category=Torrent._CAT_MOVIE
    ) for i in range(nb)]


class MovieClass(unittest.TestCase):

    def setUp(self):
        self.torrents = generate_torrents(2)
        self.fake_imdb_movie = imdb.Movie.Movie(movieID='123')

    def test_init_class(self):

        movie = Movie("123", self.torrents)
        self.assertIsInstance(movie, Movie)

        movie = Movie(123, self.torrents)
        self.assertIsInstance(movie, Movie)

        with self.assertRaises(TypeError):
            Movie(123, "torrent_id")

        with self.assertRaises(TypeError):
            torrents = self.torrents.copy()
            torrents.append("torrent_str")
            Movie(123, torrents)

        with self.assertRaises(ValueError):
            torrents = self.torrents.copy()
            torrents[1]._category = Torrent._CAT_SERIE
            Movie(123, torrents)

    @patch('mediastrends.tools.movies.get_imdb_resource', side_effect=imdb.IMDbError)
    def test_imdb_resource_error(self, mock):

        movie = Movie("7829839387", self.torrents)
        movie._RETRIES = 0
        with self.assertRaises(ValueError):
            movie.imdb_resource

    @patch('mediastrends.tools.movies.get_imdb_resource')
    def test_imdb_resource_correct(self, mock):
        self.fake_imdb_movie.set_data({'title': 'titre_1', 'cover url': 'https://m.media-amazon.com/images/M/MV5BZWY0MTYzODEtODI4ZS00YjkxLWJmMTctODRkY2M1ZTg3MTUxXkEyXkFqcGdeQXVyMTMxNDY5Nw@@._V1_SY150_CR4,0,101,150_.jpg'})
        mock.return_value = self.fake_imdb_movie

        full_size_cover = 'https://m.media-amazon.com/images/M/MV5BZWY0MTYzODEtODI4ZS00YjkxLWJmMTctODRkY2M1ZTg3MTUxXkEyXkFqcGdeQXVyMTMxNDY5Nw@@.jpg'

        movie = Movie("123", self.torrents)

        self.assertEqual(movie.imdb_resource.movieID, movie.imdb_id)
        self.assertEqual(self.fake_imdb_movie['title'], movie.title)
        self.assertEqual(self.fake_imdb_movie['full-size cover url'], movie.cover_url)
        self.assertEqual(full_size_cover, movie.cover_url)

    @patch('mediastrends.tools.movies.get_imdb_resource')
    def test_imdb_resource_correct_no_data(self, mock):
        mock.return_value = self.fake_imdb_movie

        movie = Movie("123", self.torrents)
        with self.assertRaises(ValueError):
            movie.title
        with self.assertRaises(ValueError):
            movie.cover_url

    def test_extras_attributes(self):
        movie = Movie("123", self.torrents)
        data = {'cover_url': 'cover_url', 'title': 'Titre_1'}
        movie._extras.update(data)

        self.assertEqual(data.get('cover_url'), movie.cover_url)
        self.assertEqual(data.get('title'), movie.title)


class MovieCreation(unittest.TestCase):

    def setUp(self):
        self.torrents = generate_torrents(10)
        self.torrents[0].name = 'Titre Film Long (sous titre) (2020).MULTi.VFF.2160p.10bit.4KLight.WEB.HDR10.BluRay.x265.AC3.5.1.Portos'
        self.torrents[1].name = 'Titre film long 2020 TRUEFRENCH HDRiP MD'
        self.torrents[2].name = 'titre.film.long.2020.FRENCH.BRRip.XviD.AC3-NoTag'
        self.torrents[3].name = '[EQUIPE] Titre Film LONG (2020) 720p WEBRip'
        self.torrents[4].name = 'Titre du film qui à rien à voir'
        self.torrents[5].name = 'movie title (2019) VO 720p WEBRip stéréo x265 HEVC-PSA'
        self.torrents[6].name = 'MOVIE title - 2019 - MULTI - WEBRIP - 2160P - 8BITS - 4K - X265'
        self.torrents[7].name = 'U-235 2019 MULTi 1080p WEB H264-NLX5'
        self.torrents[8].name = 'name 2'

        self.fake_groups = {
            'titre film long': {
                'torrents': self.torrents[:2],
                'parsed_titles': ['titre film long'],
                'parsed_names': [{'year': 2020}, {'year': 2019}]
            },
            'titre film long2': {
                'torrents': [self.torrents[3]],
                'parsed_titles': ['titre film long2'],
                'parsed_names': [{'year': 2020}]
            }
        }

    def test_group_torrents_by_name(self):
        groups = tools_m.group_torrents_by_name(self.torrents)

        self.assertIsInstance(groups, dict)
        self.assertCountEqual(groups.keys(), ['titre film long', 'titre du film qui à rien à voir', 'movie title', 'u-235', 'name', 'name 2'])

    @patch("imdb.IMDb")
    def test_movie_from_title(self, ia_mock):
        imdb_movie = imdb.Movie.Movie(movieID='123')
        imdb_movie.set_data({'kind': 'movie', 'year': 2020})
        instance = ia_mock.return_value
        instance.search_movie.return_value = [
            imdb_movie
        ]
        results = movies_from_title("title")

        self.assertIsInstance(results, list)
        self.assertEqual(results[0].imdb_id, "123")

        instance.search_movie.return_value = []
        results = movies_from_title("title")
        self.assertIsInstance(results, list)

    @patch("mediastrends.torrent.Movie.movies_from_title")
    def test_movies_from_group_torrents(self, mock):
        fake_movie_1 = Movie(imdb_id='123')
        fake_movie_1._extras['year'] = 2020
        fake_movie_2 = Movie(imdb_id='123')
        fake_movie_2._extras['year'] = 2019
        mock.return_value = [fake_movie_1, fake_movie_2]

        movies = movies_from_group_torrents(self.fake_groups)

        self.assertIsInstance(movies, list)
        self.assertEqual(movies[0].imdb_id, '123')
        self.assertEqual(len(movies[0].torrents), 3)

        mock.return_value = []

        movies = movies_from_group_torrents(self.fake_groups)
        self.assertEqual([], movies)
