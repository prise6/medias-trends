"""
DEPRECATED : use of Jackett + Torznab specification
"""

import re
import datetime

from .YggRSS import YggRSS
from mediastrends.torrent.Page import Page
from mediastrends.torrent.Torrent import Torrent
import mediastrends.tools as tools


class YggPage(Page):

    def __init__(self, url, soup=None):
        self._sub_cat = None
        super().__init__(url, soup)

    @property
    def info_hash(self):
        if not self._info_hash:
            self._info_hash = self.soup.select_one('#informationsContainer .informations tr:nth-of-type(5) td:last-child').get_text()
        return self._info_hash

    @info_hash.setter
    def info_hash(self, info_hash):
        self._info_hash = info_hash
        return self

    @property
    def pub_date(self):
        if not self._pub_date:
            pub_date_text = self.soup.select_one('#informationsContainer tr:nth-of-type(7) td:last-child').get_text()
            match = re.search(r'(\d+/\d+/\d+ \d+:\d+)', pub_date_text)
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
            full_name = self.soup.select_one('#informationsContainer tr:nth-of-type(1) td:last-child').get_text()
            self._name = full_name
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

    @property
    def sub_cat(self):
        if not self._sub_cat:
            div = self.soup.select_one('#informationsContainer tr:nth-of-type(3) td:last-child a div')
            self._sub_cat = 0
            if div.has_attr('class'):
                match = re.search(r'(\d+)', ' '.join(div['class']))
                self._sub_cat = int(match.group(1)) if match else 0
        return self._sub_cat

    @property
    def category(self):
        sub_cat = self.sub_cat
        if sub_cat in [2183]:
            return Torrent._CAT_MOVIE
        elif sub_cat in [2184]:
            return Torrent._CAT_SERIE
        else:
            return Torrent._CAT_UNKNOWN


#
# use python way to create "classmethod"
#


def yggpage_from_rss_item(ygg_rss: YggRSS, idx: int, populate=True):
    """
    Return YggPage object from object YggRSS specifying index item
    """
    item = ygg_rss.items[idx]
    ygg_page = YggPage(item['link'])
    if populate:
        ygg_page.pub_date = item['pub_date']
        ygg_page.name = item['name']

    return ygg_page
