from abc import ABC, abstractmethod, abstractstaticmethod

from mediastrends import logger_app, config
import mediastrends.tools as tools


class Page(ABC):

    _HEADERS = {}
    _HEADERS['user-agent'] = config.get('requests', 'user_agent')

    def __init__(self, url, soup = None):
        self.url = url
        self._soup = soup
        self._name = None
        self._pub_date = None
        self._seeders = None
        self._leechers = None
        self._completed = None
        self._size = None
        self._hash_info = None

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = tools.quote_url(url)
        return self

    @property
    def soup(self):
        if not self._soup:
            logger_app.info("Let's scrap page: %s", self._url)
            self.soup = tools.parsed_html_content(self._url, headers = self._HEADERS)
        return self._soup

    @soup.setter
    def soup(self, soup):
        self._soup = soup
        return self

    @property
    @abstractmethod
    def hash_info(self):
        return

    @property
    @abstractmethod
    def pub_date(self):
        return

    @property
    @abstractmethod
    def name(self):
        return

    @property
    @abstractmethod
    def size(self):
        return

    @property
    @abstractmethod
    def seeders(self):
        return

    @property
    @abstractmethod
    def leechers(self):
        return

    @property
    @abstractmethod
    def completed(self):
        return