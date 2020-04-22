import unittest
from unittest.mock import patch
import datetime
import imdb
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Movie import Movie


class MovieClass(unittest.TestCase):

    def setUp(self):
        self.torrents = [
            Torrent("85be94b120becfb44f94f97779c61633c7647629", "name_1",
                    size=200, pub_date=datetime.datetime.now(), category=Torrent._CAT_MOVIE),
            Torrent("85be94b120becfb44f94f97779c61633c7647628", "name_2",
                    size=350, pub_date=datetime.datetime.now(), category=Torrent._CAT_MOVIE)
        ]
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
