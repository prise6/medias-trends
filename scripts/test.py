import datetime
import pytz
import re
import mediastrends
import mediastrends.ygg as ygg
from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PTorrent import PTorrent 
from mediastrends.database.peewee.PTracker import PTracker
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker


# torrent = PDbManager.get_torrent_by_hash("2fef114edc5f41e7310c8c4b89044d8e90759bba")
# torrent = PDbManager.get_torrent_by_hash("d0e2970cc29d79ae8338e25b7f0da4773d6e711b")
try:
    for db_torrent in PTorrent.select():
        torrent = PDbManager.db_to_torrent(db_torrent)
        stats_collection = PDbManager.get_stats_collection(torrent)
        
        if stats_collection.is_trending():
            print(torrent)
            print(stats_collection)
            # print(stats_collection.dataframe)
        
except Exception as err:
    logger_app.error(err)

