import logging
import logging.config
import mediastrends.tools.config as cfg
from mediastrends.database.peewee.PDatabaseFactory import PDatabaseFactory


#
# Logging
#

logging.getLogger(__name__).addHandler(logging.NullHandler())


#
# Configuration
#

config = cfg.populate_config(cfg.init_config(), reload_=False)
trackers_config = cfg.read_trackers_file(config)
indexers_config = cfg.read_indexers_file(config)

#
# Database
#

db_factory = PDatabaseFactory(config)

#
# Global variables
#

CATEGORY_NAME = {
    'movies': 1,
    'series': 2,
    'unknown': 0
}

STATUS_NAME = {
    'unfollow': 0,
    'new': 1,
    'follow': 2,
}
