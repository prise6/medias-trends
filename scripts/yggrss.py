import os
from datetime import datetime
from time import mktime

from mediastrends import config, db
from mediastrends.database.peewee.PDbManager import PDbManager
import mediastrends.ygg as ygg


rss_file = os.path.join(config.get('directory', 'data'), 'rss_ygg.xml')
ygg_rss = ygg.rss_from_feedparser(rss_file)
ygg_page = ygg.page_from_rss_item(ygg_rss, 5)
ygg_torrent = ygg.torrent_from_page(ygg_page)

print(ygg_torrent.hash_info)

PDbManager.save_torrent(ygg_torrent)
