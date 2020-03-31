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
        trends_manager = TrendsManager(config, PDbManager)
        
        trends_manager.evaluate(ClassicTrendsEngine())
        trends_manager.save_trends()
    except ValueError as err:
        logger_app.info("Aucun torrent dans la categorie")


if __name__ == '__main__':
    main()
