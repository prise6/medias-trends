import datetime
from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PDbManager import PDbManager
import mediastrends.stats as stats
import mediastrends.ygg as ygg
from mediastrends.trends.TrendsManager import TrendsManager
from mediastrends.trends.TrendsEngine import ClassicTrendsEngine


def main():
    torrents = PDbManager.get_torrents_by_status([0, 1, 2], 2)
    logger_app.info("Torrents number %s", len(torrents))
    trends_manager = TrendsManager(config)
    
    stats_collections = [PDbManager.get_stats_collection(t) for t in torrents]
    logger_app.info("Stats collections number %s", len(stats_collections))

    trends_manager.evaluate(stats_collections, ClassicTrendsEngine())
    
    is_trending = trends_manager.is_trending
    for stats_col in is_trending:
        try:
            PDbManager.save_stats_collection_as_trends(stats_col)
            for torrent in stats_col.torrents:
                print("%s / score : %s" % (str(torrent), stats_col.score))
        except Exception as err:
            logger_app.error(err)
            

if __name__ == '__main__':
    main()
