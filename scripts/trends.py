from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PDbManager import PDbManager
import mediastrends.stats as stats
import mediastrends.ygg as ygg


def main():
    stats_manager = stats.StatsManager(config, PDbManager)
    torrents = stats_manager.get_torrents_by_tracker(ygg.tracker)

    for torrent in torrents:
        stats_collection = PDbManager.get_stats_collection(torrent)
        
        if stats_collection.is_trending():
            print(torrent)
            print(stats_collection)


if __name__ == '__main__':
    main()
