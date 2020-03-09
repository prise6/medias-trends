import datetime
import mediastrends
from mediastrends import config, db
from mediastrends.database.peewee.PTorrent import PTorrent, PTorrentTracker 
from mediastrends.database.peewee.PTracker import PTracker
from mediastrends.database.peewee.PPage import PPage
from mediastrends.database.peewee.PStats import PStats
from mediastrends.database.peewee.PDbManager import PDbManager


db.connect()
db.drop_tables([PTorrent, PTracker, PPage, PTorrentTracker, PStats], safe=True)
db.create_tables([PTorrent, PTracker, PPage, PTorrentTracker, PStats])

PTorrent._schema.truncate_table()
PTracker._schema.truncate_table()
PPage._schema.truncate_table()
PTorrentTracker._schema.truncate_table()
PStats._schema.truncate_table()