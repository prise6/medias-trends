import mediastrends
from mediastrends import config, db
from mediastrends.database.peewee.PTorrent import PTorrent 
from mediastrends.database.peewee.PTracker import PTracker

# PTracker()
db.connect()
db.create_tables([PTorrent, PTracker])

