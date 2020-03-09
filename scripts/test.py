import datetime
import mediastrends
import mediastrends.ygg as ygg
from mediastrends import config, db
from mediastrends.database.peewee.PTorrent import PTorrent 
from mediastrends.database.peewee.PTracker import PTracker
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.Torrent import Torrent
from mediastrends.torrent.Tracker import Tracker


pdb_manager = PDbManager(config, db)


ygg_torrent = Torrent(
    hash_info = "116d3df019e7fcee7dd107fbdb70654af4256de5",
    name = "Charlies.Angels.2019.REPACK.MULTi.1080p.HDLight.x264.AC3-EXTREME",
    pub_date = datetime.date.today(),
    size = 6090000000
)

tmp = PDbManager.save_torrent_tracker(ygg_torrent, ygg.tracker)

print(type(tmp))

db.close()
