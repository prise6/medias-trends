from mediastrends import config, db, logger_app
from mediastrends.database.peewee.PDbManager import PDbManager
import mediastrends.stats as stats
import mediastrends.ygg as ygg

def main():
    ## update status
    stats_manager = stats.StatsManager(config, PDbManager)
    stats_manager.update_torrents_status()

if __name__ == '__main__':
    main()