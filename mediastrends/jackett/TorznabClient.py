import urllib.parse
import requests
import logging

logger = logging.getLogger(__name__)


class TorznabJackettClient():

    def __init__(self, config):
        self._config = config
        self._indexer = None
        self._params = {
            'action': '',
            'q': '',
            'apikey': self._config.get('jackettapi', 'apikey')
        }
        self._url = None
        self._response = None
        self.headers = {
            'user_agent': self._config.get('requests', 'user_agent')
        }
        self._rss_content = None

    @property
    def indexer(self):
        return self._indexer

    @indexer.setter
    def indexer(self, indexer: str):
        if indexer not in self._config.get('indexers', 'authorized'):
            raise NotImplementedError("%s indexer not authorized")
        self._indexer = indexer

    @property
    def action(self):
        return self._params.get('action', '')

    @action.setter
    def action(self, action: str):
        if not isinstance(action, str):
            raise TypeError('action param must be instance of string')
        if action not in ['tvsearch', 'search', 'movie']:
            raise NotImplementedError("%s action is not implemented yet")
        self.add_param('action', action)

    @property
    def query(self):
        return self._params.get('q', '')

    @query.setter
    def query(self, query: str):
        if not isinstance(query, str):
            raise TypeError('query param must be instance of string')
        self.add_param('query', query)

    def add_param(self, key, value):
        self._params.update({key: value})

    def build_url(self):
        query = urllib.parse.urlencode(self._params)

        self._url = urllib.parse.urlunsplit(
            urllib.parse.SplitResult(
                self._config.get('jackettapi', 'scheme'),
                self._config.get('jackettapi', 'netloc'),
                self._config.get('jackettapi', 'path').format(indexer=self.indexer),
                query,
                None
            )
        )

    def get(self):
        with requests.get(self._url, headers=self.headers) as req:
            self._response = req
            req.raise_for_status()

    def process(self):
        try:
            self.build_url()
            self.get()
        except requests.exceptions.HTTPError:
            error = self._response.status_code
            try:
                content = self._response.json()
                if content.get('error'):
                    error = content.get('error')
            except ValueError:
                pass
            logger.error('An error occured while contacting jacket api: %s', error)
            return self._rss_content

        return self._response.text

    def get_rss_content(self):
        if self._rss_content is None:
            self._rss_content = self.process()
        return self._rss_content
