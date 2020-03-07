from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import requests
from mediastrends import logger_app, config


class YggPage():

    def __init__(self, html):
        self._soup = BeautifulSoup(html, 'html.parser')
        self._url = None
        self._name = None
        self._category = None
        self._seeders = None
        self._leechers = None
        self._downloaded = None
        self._size = None
        self._hash_info = None

    @property
    def hash_info(self):
        if not self._hash_info:
            self._hash_info = self._soup.select_one('#informationsContainer .informations tr:nth-of-type(5) td:last-child').get_text()
        return self._hash_info

    @hash_info.setter
    def hash_info(self, hash_info):
        self._hash_info = hash_info

    def to_torrent():
        return


#
# use python way to create "classmethod"
#

def yggpage_from_link(link: str, headers = {}):

    if 'user-agent' not in headers.keys():
        headers['user-agent'] = config.get('requests', 'user_agent')

    url = urllib.parse.urlsplit(link)
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    logger_app.info("Let's scrap ygg page: %s", url)

    with requests.get(url, headers=headers) as response:
        logger_app.info('--> status code: %s' % (str(response.status_code)))
        if not response.status_code == requests.codes.ok:
            return None
        return YggPage(response.text)

    return None

