import os
from datetime import datetime
from time import mktime

from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PDbManager import PDbManager
import mediastrends.stats as stats
import mediastrends.tools as tools
import mediastrends.ygg as ygg



# rss_file = os.path.join(config.get('directory', 'data'), 'rss_ygg.xml')
# ygg_rss = ygg.rss_from_feedparser(rss_file)

ygg_rss = ygg.rss_from_feedparser(config.get('rss', 'ygg_movies'))
_N_ITEMS = len(ygg_rss.items)
torrents = []
for idx, item in enumerate(ygg_rss.items):
    logger_app.info("---> RSS item %s/%s ... " % (idx+1, _N_ITEMS))
    ygg_page = ygg.page_from_rss_item(ygg_rss, idx, True)
    ygg_torrent = ygg.torrent_from_page(ygg_page)
    torrents.append(ygg_torrent)

    db_page = PDbManager.save_page(ygg_page, ygg_torrent, ygg.tracker)
    
stats_scraper = stats.StatsScraper(ygg.tracker)
stats_scraper.torrents = torrents
stats_scraper.run()

stats_collection = stats_scraper.stats_collection
for ygg_stats in stats_collection:
    db_stats = PDbManager.save_stats(ygg_stats)


exit()
ygg_rss = ygg.rss_from_feedparser(config.get('rss', 'ygg_movies'))
_N_ITEMS = len(ygg_rss.items)
for idx, item in enumerate(ygg_rss.items):
    logger_app.info("---> RSS item %s/%s ... " % (idx+1, _N_ITEMS))

    ygg_page = ygg.page_from_rss_item(ygg_rss, idx, False)
    ygg_torrent = ygg.torrent_from_page(ygg_page)
    ygg_stats = stats.stats_from_page(ygg_page, ygg_torrent, ygg.tracker)

    db_page = PDbManager.save_page(ygg_page, ygg_torrent, ygg.tracker)
    db_stats = PDbManager.save_stats(ygg_stats)


exit()
# url = "https://www2.yggtorrent.se/torrent/filmvid%C3%A9o/film/572742-la%2Bplan%C3%A8te%2Bdes%2Bsinges%2B2001%2Bbluray%2Bx264%2B1080p%2Bvff%2Bdts%2B5%2B1%2B-%2Bvfhd?attempt=1"
# soup = tools.parsed_html_content_from_file(os.path.join(config.get('directory', 'data'), 'html_ygg_ex.html'))

# ygg_page = ygg.Page(url, soup)
# ygg_torrent = ygg.torrent_from_page(ygg_page)

# ygg_stats = stats.stats_from_page(ygg_page, ygg_torrent, ygg.tracker)
# print(ygg_stats)

# db_page = PDbManager.save_page(ygg_page, ygg_torrent, ygg.tracker)
# print(db_page)
# print(tmp)

# from bs4 import BeautifulSoup

# url = "https://www2.yggtorrent.se/torrent/filmvid%C3%A9o/film/572742-la%2Bplan%C3%A8te%2Bdes%2Bsinges%2B2001%2Bbluray%2Bx264%2B1080p%2Bvff%2Bdts%2B5%2B1%2B-%2Bvfhd?attempt=1"
# soup = tools.parsed_html_content_from_file(os.path.join(config.get('directory', 'data'), 'html_ygg_ex.html'))

# tmp = ygg.Page(url, soup)
# print(ygg_page.size)
# print(type(ygg_page.size))
