import feedparser
import re
from datetime import datetime
from time import mktime


class YggRSS:

    def __init__(self, items: list):
        """
        Initializer items as a list of dictionnaries with
        * link
        * name
        * pub_date in format datetime.datetime
        """
        self._items = items

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        self._items = items


#
# use python way to create "classmethod"
#

def yggrss_from_feedparser(argument: str):
    """
    Use feedparser to instanciate YggRSS class
    """
    d = feedparser.parse(argument)
    items = []
    for item in d['entries']:
        name = item['title']
        match = re.search(r"(.*)\(S:\d+/L:\d+\)$", name)
        try:
            name = match.group(1).strip()
        except IndexError:
            pass
        items.append({
            'link': item['link'],
            'name': name,
            'pub_date': datetime.fromtimestamp(mktime(item['published_parsed']))
        })

    return YggRSS(items)
