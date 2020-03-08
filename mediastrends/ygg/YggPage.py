from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import requests

from mediastrends import logger_app, config
from .YggRSS import YggRSS


class YggPage():

    def __init__(self, html):
        self._soup = BeautifulSoup(html, 'html.parser')
        self._url = None
        self._name = None
        self._pub_date = None
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
        return self

    @property
    def pub_date(self):
        if not self._pub_date:
            self._pub_date = self._soup.select_one('#informationsContainer .w tr:nth-of-type(7) td:last-child').get_text()
        return self._pub_date

    @pub_date.setter
    def pub_date(self, pub_date):
        self._pub_date = pub_date
        return self

    @property
    def name(self):
        if not self._name:
            self._name = self._soup.select_one('#informationsContainer .w tr:nth-of-type(1) td:last-child').get_text()
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        return self

#
# use python way to create "classmethod"
#

def yggpage_from_link(link: str, headers = {}):
    """
    Return YggPage object from link
    """

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

def yggpage_from_rss_item(ygg_rss: YggRSS, idx: int, headers = {}):
    """
    Return YggPage object from object YggRSS specifying index item
    """
    item = ygg_rss.items[idx]
    ygg_page = yggpage_from_link(item['link'], headers)
    ygg_page.pub_date = item['pub_date']
    ygg_page.name = item['name']
    
    return ygg_page