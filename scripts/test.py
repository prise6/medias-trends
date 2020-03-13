import datetime
import pytz
import re
import mediastrends
import mediastrends.ygg as ygg
import mediastrends.stats as stats
import mediastrends.tools as tools
from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PTorrent import PTorrent 
from mediastrends.database.peewee.PTracker import PTracker
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker


# torrent = PDbManager.get_torrent_by_hash("2fef114edc5f41e7310c8c4b89044d8e90759bba")
# torrent = PDbManager.get_torrent_by_hash("d0e2970cc29d79ae8338e25b7f0da4773d6e711b")

try:
    res = PDbManager.get_torrents_by_status(2)

    # torrent = PDbManager.torrent_to_db(res[0])
    # torrent.status = 2
    
    torrent = res[0]
    torrent.unfollow()
    db_torrent, _ = PDbManager.update(torrent)
    exit()

except Exception as err:
    logger_app.error(err)


try:
    torrents = [PDbManager.db_to_torrent(db_torrent) for db_torrent in PTorrent.select()]
    stats_scraper = stats.StatsScraper(ygg.tracker)
    stats_scraper.torrents = torrents
    stats_scraper.run_by_batch()

    stats_collection = stats_scraper.stats_collection
    for ygg_stats in stats_collection:
        db_stats = PDbManager.save_stats(ygg_stats)
except Exception as err:
    logger_app.error(err)

try:
    for torrent in torrents:
        stats_collection = PDbManager.get_stats_collection(torrent)
        
        if stats_collection.is_trending():
            print(torrent)
            print(stats_collection)
        
except Exception as err:
    logger_app.error(err)

