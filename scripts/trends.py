from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PDbManager import PDbManager
import mediastrends.stats as stats
import mediastrends.ygg as ygg
from mediastrends.trends.TrendsManager import TrendsManager
from mediastrends.trends.TrendsEngine import ClassicTrendsEngine


def main():
    torrents = PDbManager.get_torrents_by_status([0, 1, 2], 1)

    stats_manager = stats.StatsManager(config, PDbManager)
    trends_manager = TrendsManager(config, PDbManager)
    
    stats_collections = [stats_manager.get_stats_collection(t) for t in torrents]

    trends_manager.evaluate(stats_collections, ClassicTrendsEngine())

    is_trending = trends_manager.is_trending
    for stats_col in is_trending:
        print(stats_col)

if __name__ == '__main__':
    main()
