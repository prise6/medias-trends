from mediastrends.database.peewee.PDbManager import PDbManager
from mediastrends import config, db, logger_app
import mediastrends.ygg as ygg


def main():

    ygg_rss = ygg.rss_from_feedparser(config.get('rss', 'ygg_movies'))
    _N_ITEMS = len(ygg_rss.items)
    torrents = []
    for idx, item in enumerate(ygg_rss.items):
        logger_app.info("---> RSS item %s/%s ... " % (idx+1, _N_ITEMS))
        ygg_page = ygg.page_from_rss_item(ygg_rss, idx, True)
        ygg_torrent = ygg.torrent_from_page(ygg_page)
        torrents.append(ygg_torrent)

        db_page = PDbManager.save_page(ygg_page, ygg_torrent, ygg.tracker)


if __name__ == '__main__':
    main()
