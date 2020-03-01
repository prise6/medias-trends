import os
import yaml
import logging
import logging.config
import configparser
from configparser import ExtendedInterpolation


##
## Logging
##

with open(os.path.join(os.getenv('WORKDIR'), 'config', 'logging_%s.yaml' % os.getenv('MODE')), 'rt') as cfg_file:
    logging.config.dictConfig(yaml.unsafe_load(cfg_file.read()))

logger_app = logging.getLogger('app')

##
## Configuration
##
logger_app.info('Init config ...')
config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
config.read(os.path.join(os.getenv('WORKDIR'), 'config', 'config_%s.ini' % os.getenv('MODE')))
