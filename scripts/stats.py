from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PDbManager import PDbManager
import mediastrends.stats as stats
import mediastrends.ygg as ygg


def main():
   
    ## tracker ygg
    torrents = PDbManager.get_torrents_by_tracker(ygg.tracker, status = [1, 2], category = [2])
    logger_app.info("Torrents number: %s", len(torrents))
    stats_scraper = stats.StatsScraper(ygg.tracker)
    stats_scraper.torrents = torrents
    stats_scraper.run_by_batch()

    stats_collection = stats_scraper.stats_collection
    logger_app.info("Stats number: %s", stats_collection.count())

    for ygg_stats in stats_collection.stats:
        db_stats = PDbManager.save_stats(ygg_stats)

if __name__ == '__main__':
    main()
