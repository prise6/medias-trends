import os
from datetime import datetime
from time import mktime

from mediastrends import config, db
import mediastrends.tools as tools
from mediastrends.database.peewee.PDbManager import PDbManager
import mediastrends.ygg as ygg


rss_file = os.path.join(config.get('directory', 'data'), 'rss_ygg.xml')
ygg_rss = ygg.rss_from_feedparser(rss_file)
ygg_page = ygg.page_from_rss_item(ygg_rss, 1)
ygg_torrent = ygg.torrent_from_page(ygg_page)

tmp = PDbManager.save_page(ygg_page, ygg_torrent)
print(tmp)
tmp = PDbManager.save_torrent(ygg_torrent, True, True)
print(tmp)

tmp = PDbManager.get_torrent_by_hash("ou")
print(tmp)

# from bs4 import BeautifulSoup

# url = "https://www2.yggtorrent.se/torrent/filmvid%C3%A9o/film/572742-la%2Bplan%C3%A8te%2Bdes%2Bsinges%2B2001%2Bbluray%2Bx264%2B1080p%2Bvff%2Bdts%2B5%2B1%2B-%2Bvfhd?attempt=1"
# soup = tools.parsed_html_content_from_file(os.path.join(config.get('directory', 'data'), 'html_ygg_ex.html'))

# tmp = ygg.Page(url, soup)
# print(ygg_page.size)
# print(type(ygg_page.size))
