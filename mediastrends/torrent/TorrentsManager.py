import datetime
import logging
from mediastrends import STATUS_NAME
from mediastrends.database.DbManager import DbManager
from mediastrends.torrent.Torrent import Torrent

logger = logging.getLogger(__name__)


class TorrentsManager():

    def __init__(self, config, dbmanager: DbManager, category: list = None):
        self.cfg = config
        self._dbmanager = dbmanager
        self._category = category
        self._torrents_trending = []
        self._torrents_trending_lookup = []
        self._torrents_candidates = []

        self._max_date = self.cfg.getdatetime('torrents_manager', 'max_date', fallback=None)
        self._delta_hours = self.cfg.getint('torrents_manager', 'delta_hours', fallback=1)
        self._min_date = self.cfg.getdatetime('torrents_manager', 'min_date', fallback=None)
        self._candidates_status = [STATUS_NAME[s] for s in self.cfg.getlist('torrents_manager', 'candidates_status', fallback=['new', 'follow'])]
        self._new_delay = self.cfg.getint('stats_manager', 'new_delay', fallback=3)

    @property
    def torrents_candidates(self):
        if not self._torrents_candidates:
            try:
                self._torrents_candidates = self._dbmanager.get_torrents_by_status(
                    status=self._candidates_status,
                    category=self._category
                )
            except ValueError:
                logger.warning("Candidate torrents are empty.")

        return self._torrents_candidates

    @property
    def torrents_trending(self):
        if not self._torrents_trending:
            try:
                self._torrents_trending = self._dbmanager.get_trending_torrents_by_category(
                    category=self._category,
                    min_date=self._min_date,
                    max_date=self._max_date,
                    delta_hours=self._delta_hours
                )
            except ValueError:
                logger.warning("Trending torrents are empty")
        return self._torrents_trending

    @property
    def torrents_trending_lookup(self):
        if not self._torrents_trending_lookup:
            self._torrents_trending_lookup = [t.info_hash for t, _, _ in self.torrents_trending]
        return self._torrents_trending_lookup

    @torrents_candidates.setter
    def torrents_candidates(self, torrents_candidates: list):
        self._torrents_candidates = torrents_candidates
        return self

    @torrents_trending.setter
    def torrents_trending(self, torrents_trending: list):
        self._torrents_trending = torrents_trending
        return self

    def compute_torrents_status(self):
        """
        From new and follow torrents, compute which are not welcome anymore
        """
        today = datetime.datetime.today()

        nb_new = 0
        nb_new_follow = 0

        nb_follow = 0
        nb_follow_unfollow = 0

        for torrent in self.torrents_candidates:
            if torrent.status == Torrent._STATUS_NEW:
                nb_new += 1
                if (today - torrent.pub_date).days >= self._new_delay:
                    if torrent.info_hash in self.torrents_trending_lookup:
                        nb_new_follow += 1
                        torrent.follow()
                    else:
                        torrent.unfollow()
            elif torrent.status == Torrent._STATUS_FOLLOW:
                nb_follow += 1
                if torrent.info_hash not in self.torrents_trending_lookup:
                    nb_follow_unfollow += 1
                    torrent.unfollow()

        logger.debug("New torrents (%s) to follow: %s", nb_new, nb_new_follow)
        logger.debug("Follow torrents (%s) to keep: %s", nb_follow, nb_follow - nb_follow_unfollow)

        return self

    def update_torrents_status(self):
        """
        only torrents follow and unfollow has to be updated
        """
        self.compute_torrents_status()
        nb_rows_updated = 0
        for torrent in self.torrents_candidates:
            _, c = self._dbmanager.update(torrent)
            nb_rows_updated += c

        return nb_rows_updated
