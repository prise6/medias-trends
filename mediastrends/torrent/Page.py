from abc import ABC
import logging
import datetime
from retry.api import retry_call

from mediastrends import config
import mediastrends.tools as tools

logger = logging.getLogger(__name__)


class Page(ABC):

    _HEADERS = {}
    _HEADERS['user-agent'] = config.get('requests', 'user_agent')
    _RETRIES = config.getint('retry', 'tries')
    _DELAY = config.getint('retry', 'delay')

    def __init__(self, url, soup=None):
        self.url = url
        self._soup = soup
        self._name = None
        self._pub_date = None
        self._seeders = None
        self._leechers = None
        self._completed = None
        self._size = None
        self._info_hash = None
        self._valid_date = None

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = tools.quote_url(url)
        return self

    @property
    def valid_date(self, valid_date):
        return self.valid_date

    @valid_date.setter
    def valid_date(self, valid_date: datetime.datetime):
        if not isinstance(valid_date, datetime.datetime):
            raise ValueError("valid_date (%s) should be datetime object", valid_date)

        self._valid_date = valid_date.replace(microsecond=0)
        return self

    @property
    def soup(self):
        if not self._soup:
            logger.debug("Scraping page: %s", self._url)
            # self.soup = tools.parsed_html_content(self._url, headers = self._HEADERS)
            self.soup = retry_call(tools.parsed_html_content, fkwargs={"url": self._url, "headers": self._HEADERS}, tries=self._RETRIES, delay=self._DELAY, jitter=(3, 10), logger=logger)
        return self._soup

    @soup.setter
    def soup(self, soup):
        self._soup = soup
        self.valid_date = datetime.datetime.now()
        return self

    @property
    def info_hash(self):
        raise NotImplementedError

    @property
    def pub_date(self):
        raise NotImplementedError

    @property
    def name(self):
        raise NotImplementedError

    @property
    def size(self):
        raise NotImplementedError

    @property
    def seeders(self):
        raise NotImplementedError

    @property
    def leechers(self):
        raise NotImplementedError

    @property
    def completed(self):
        raise NotImplementedError

    @property
    def category(self):
        raise NotImplementedError
