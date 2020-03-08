import urllib.request
import urllib.parse
import requests
import re
import datetime

from mediastrends import logger_app, config
from .YggRSS import YggRSS
from mediastrends.torrent.Page import Page
import mediastrends.tools as tools


class YggPage(Page):

    def __init__(self, url, soup = None):
        self._category = None
        super().__init__(url, soup)

    @property
    def hash_info(self):
        if not self._hash_info:
            self._hash_info = self.soup.select_one('#informationsContainer .informations tr:nth-of-type(5) td:last-child').get_text()
        return self._hash_info

    @hash_info.setter
    def hash_info(self, hash_info):
        self._hash_info = hash_info
        return self

    @property
    def pub_date(self):
        if not self._pub_date:
            pub_date_text = self.soup.select_one('#informationsContainer tr:nth-of-type(7) td:last-child').get_text()
            match = re.search('(\d+/\d+/\d+ \d+:\d+)', pub_date_text)
            pub_date = datetime.datetime.strptime(match.group(1), "%d/%m/%Y %H:%M")
            self._pub_date = pub_date
        return self._pub_date

    @pub_date.setter
    def pub_date(self, pub_date):
        self._pub_date = pub_date
        return self

    @property
    def name(self):
        if not self._name:
            self._name = self.soup.select_one('#informationsContainer tr:nth-of-type(1) td:last-child').get_text()
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        return self
    
    @name.setter
    def name(self, name):
        self._name = name
        return self

    @property
    def size(self):
        if not self._size:
            size_str = self.soup.select_one('#informationsContainer tr:nth-of-type(4) td:last-child').get_text()
            self._size = tools.parse_size(size_str)
        return self._size

    @size.setter
    def size(self, size):
        self._size = size
        return self

    @property
    def seeders(self):
        if not self._seeders:
            self._seeders = int(self.soup.select_one('#adv_search_cat td:nth-of-type(2)').get_text())
        return self._seeders

    @property
    def leechers(self):
        if not self._leechers:
            self._leechers = int(self.soup.select_one('#adv_search_cat td:nth-of-type(4)').get_text())
        return self._leechers

    @property
    def completed(self):
        if not self._completed:
            self._completed = int(self.soup.select_one('#adv_search_cat td:nth-of-type(6)').get_text())
        return self._completed


#
# use python way to create "classmethod"
#


def yggpage_from_rss_item(ygg_rss: YggRSS, idx: int):
    """
    Return YggPage object from object YggRSS specifying index item
    """
    item = ygg_rss.items[idx]
    ygg_page = YggPage(item['link'])
    ygg_page.pub_date = item['pub_date']
    ygg_page.name = item['name']
    
    return ygg_page