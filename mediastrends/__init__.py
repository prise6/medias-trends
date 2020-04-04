import os
import logging
import logging.config
import mediastrends.tools.config as cfg
from mediastrends.database.peewee.PDatabaseFactory import PDatabaseFactory
from mediastrends.torrent.Torrent import Torrent

##
## Logging
##

logging.getLogger(__name__).addHandler(logging.NullHandler())


##
## Configuration
##

config = cfg.populate_config(cfg.init_config(), reload_ = False)

##
## Database
##

db_factory = PDatabaseFactory(config)

##
## Global variables
##

CATEGORY_NAME = {
    'movies': Torrent._CAT_MOVIE,
    'series': Torrent._CAT_SERIE,
    'unknown': Torrent._CAT_UNKNOWN
}