import os
import yaml
import logging
import logging.config
import mediastrends.tools.config as cfg
from mediastrends.database.peewee.PDatabaseFactory import PDatabaseFactory
from mediastrends.torrent.Torrent import Torrent


##
## Logging
##

# with open(os.path.join(os.getenv('WORKDIR'), 'config', 'logging_%s.yaml' % os.getenv('MODE')), 'rt') as cfg_file:
#     logging.config.dictConfig(yaml.unsafe_load(cfg_file.read()))

logger_app = logging.getLogger('app')

##
## Configuration
##

logger_app.info('Init config ...')
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