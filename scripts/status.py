from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends.torrent.TorrentsManager import TorrentsManager
import mediastrends.ygg as ygg

def main():
    ## update status
    torrents_manager = TorrentsManager(config, PDbManager)
    torrents_manager.update_torrents_status()

if __name__ == '__main__':
    main()