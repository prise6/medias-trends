from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PDbManager import PDbManager
import mediastrends.stats as stats
import mediastrends.ygg as ygg


def main():
    stats_manager = stats.StatsManager(config, PDbManager)
    
    ## tracker ygg
    torrents = stats_manager.get_torrents_by_tracker(ygg.tracker)
    stats_scraper = stats.StatsScraper(ygg.tracker)
    stats_scraper.torrents = torrents
    stats_scraper.run_by_batch()

    stats_collection = stats_scraper.stats_collection
    for ygg_stats in stats_collection:
        db_stats = PDbManager.save_stats(ygg_stats)

if __name__ == '__main__':
    main()
