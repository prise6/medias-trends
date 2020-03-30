import datetime
from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PDbManager import PDbManager
import mediastrends.stats as stats
import mediastrends.ygg as ygg
from mediastrends.trends.TrendsManager import TrendsManager
from mediastrends.trends.TrendsEngine import ClassicTrendsEngine
from mediastrends.torrent.Torrent import Torrent


def main():
    try:
        torrents = PDbManager.get_torrents_by_status([Torrent._STATUS_NEW, Torrent._STATUS_FOLLOW])
        logger_app.info("Torrents number %s", len(torrents))
        trends_manager = TrendsManager(config, PDbManager)
        
        stats_collections = [PDbManager.get_stats_collection(t) for t in torrents]
        logger_app.info("Stats collections number %s", len(stats_collections))

        trends_manager.evaluate(stats_collections, ClassicTrendsEngine())
        trends_manager.save_trends()
    except ValueError as err:
        logger_app.info("Aucun torrent dans la categorie")


if __name__ == '__main__':
    main()
