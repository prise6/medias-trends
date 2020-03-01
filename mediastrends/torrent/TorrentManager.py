from mediastrends.database.DbManager import DbManager
from .Torrent import Torrent
from .MovieTorrent import MovieTorrent
from .Tracker import Tracker


class TorrentManager:

    def __init__(self, config, db_manager: DbManager):
        self.cfg = config
        self.db_manager = db_manager
