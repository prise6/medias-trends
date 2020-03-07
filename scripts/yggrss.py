import os
from datetime import datetime
from time import mktime
from mediastrends.ygg.YggRSS import yggrss_from_feedparser
from mediastrends.ygg.YggPage import yggpage_from_link

from mediastrends import config



rss_file = os.path.join(config.get('directory', 'data'), 'rss_ygg.xml')
ygg_rss = yggrss_from_feedparser(rss_file)


ygg_page = yggpage_from_link(ygg_rss.items[10]['link'])
print(ygg_page.hash_info)
