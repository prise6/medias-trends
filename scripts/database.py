import datetime
import mediastrends
from mediastrends import config, db
from mediastrends.database.peewee.PTorrent import PTorrent 
from mediastrends.database.peewee.PTracker import PTracker
from mediastrends.database.peewee.PPage import PPage
from mediastrends.database.peewee.PDbManager import PDbManager


db.connect()
db.drop_tables([PTorrent, PTracker, PPage], safe=True)
db.create_tables([PTorrent, PTracker, PPage])

PTorrent._schema.truncate_table()
PTracker._schema.truncate_table()
PPage._schema.truncate_table()