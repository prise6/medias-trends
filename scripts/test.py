import datetime
import mediastrends
from mediastrends import config, db
from mediastrends.database.peewee.PTorrent import PTorrent 
from mediastrends.database.peewee.PTracker import PTracker
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker

db.connect()
db.drop_tables([PTorrent, PTracker], safe=True)
db.create_tables([PTorrent, PTracker])

PTorrent._schema.truncate_table()
PTracker._schema.truncate_table()

pdb_manager = PDbManager(config, db)

ygg_tracker = Tracker(
    scheme = config.get('ygg', 'scheme'),
    netloc = config.get('ygg', 'netloc'),
    path = config.get('ygg', 'path'),
    name = 'ygg'
)

ygg_torrent = Torrent(
    hash_info = "116d3df019e7fcee7dd107fbdb70654af4256de5",
    tracker = ygg_tracker,
    name = "Charlies.Angels.2019.REPACK.MULTi.1080p.HDLight.x264.AC3-EXTREME",
    pub_date = datetime.date.today()
)

PDbManager.save_torrent(ygg_torrent)

db.close()
