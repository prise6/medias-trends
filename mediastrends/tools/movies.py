from typing import List
import logging
from mediastrends.torrent.Torrent import Torrent
import imdb
import PTN
import textdistance
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize

logger = logging.getLogger(__name__)


def get_imdb_access(**kwargs):
    kwargs['reraiseExceptions'] = True
    return imdb.IMDb(**kwargs)


def get_imdb_resource(type_: str = 'movie', id_: int = None, imdb_access=None):
    if id_ is None:
        raise ValueError("Id must be given")
    if imdb_access is None:
        imdb_access = get_imdb_access()
    if type_ == 'movie':
        return imdb_access.get_movie(id_, info=['main'])


def group_torrents_by_name(torrents: List[Torrent]) -> dict:
    if not all([isinstance(t, Torrent) for t in torrents]):
        raise TypeError("List must only have Torrent instance")

    groups = {}
    torrents_name = [t.name for t in torrents]
    torrents_name_parsed = [PTN.parse(name) for name in torrents_name]
    torrents_name_parsed_title = []
    for idx, el in enumerate(torrents_name_parsed):
        title = el.get('title', None)
        if not (title and title.strip() != ''):
            title = torrents_name[idx]
        torrents_name_parsed_title.append(title.lower())

    nb_torrents = len(torrents_name_parsed)
    similarity_matrix = np.zeros((nb_torrents, nb_torrents))
    np.fill_diagonal(similarity_matrix, 0)

    for i in range(nb_torrents):
        for j in range(i):
            similarity_matrix[j, i] = similarity_matrix[i, j] = textdistance.lcsseq.distance(torrents_name_parsed_title[i], torrents_name_parsed_title[j])
    normalize(similarity_matrix, copy=False)

    dbscan_clusters = DBSCAN(min_samples=1, eps=.025, metric='precomputed').fit_predict(similarity_matrix)

    logger.debug('Found %s clusters for %s torrents' % (np.max(dbscan_clusters) + 1, nb_torrents))

    for cluster in np.unique(dbscan_clusters):
        idxs = np.argwhere(dbscan_clusters == cluster).flatten().tolist()
        parsed_titles_cluster = list(set([torrents_name_parsed_title[idx] for idx in idxs]))
        parsed_names_cluster = [torrents_name_parsed[idx] for idx in idxs]
        torrents_cluster = [torrents[idx] for idx in idxs]
        groups.update({parsed_titles_cluster[0]: {
            'torrents': torrents_cluster,
            'parsed_titles': parsed_titles_cluster,
            'parsed_names': parsed_names_cluster
        }})
        logger.debug("Cluster %s: %s" % (cluster, parsed_titles_cluster[0]))

    return groups
