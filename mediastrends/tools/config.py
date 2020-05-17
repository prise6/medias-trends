import os
import yaml
import datetime
import configparser
from configparser import ExtendedInterpolation


_DIRS_TO_LOOK_FOR = [
    os.getenv('MEDIASTRENDS_DIRCONF'),
    os.curdir,
    os.path.expanduser('~'),
    '/etc/mediastrends/'
]

PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
_CONFIG_FILE_NAME = 'mediastrends.%s.ini'


def init_config():
    config = configparser.ConfigParser(
        interpolation=ExtendedInterpolation(),
        converters={
            'datetime': lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M'),
            'list': lambda s: s.split(',')
        },
        allow_no_value=True
        # converters={'datetime': datetime.datetime}
    )

    return config


def populate_config(config, user_dir_config=None, mode=None, reload_=True):
    mode = mode if mode else os.getenv('MEDIASTRENDS_MODE')
    if reload_:
        for s in config.sections():
            config.remove_section(s)

    pkg_conf = look_for_package_config_file()
    if pkg_conf:
        config.read(pkg_conf)

    potential_locations = _DIRS_TO_LOOK_FOR.insert(0, user_dir_config)
    user_config = look_for_user_config_file(potential_locations, mode)

    if user_config:
        config.read(user_config)

    return config


def look_for_user_config_file(dirs=_DIRS_TO_LOOK_FOR, mode=None):
    if not mode:
        raise ValueError("Mode muse be set. export MEDIASTRENDS_MODE as environnement variable.")
    for dir_ in _DIRS_TO_LOOK_FOR:
        if dir_:
            candidat = os.path.join(dir_, _CONFIG_FILE_NAME % mode)
            if os.path.exists(candidat):
                return candidat
    raise Exception("User must override some config values. No config found.")

    return None


def look_for_package_config_file():
    theorical_conf = os.path.join(PACKAGE_DIR, 'mediastrends.ini')
    if os.path.exists(theorical_conf):
        return theorical_conf
    return None


def read_trackers_file(config):
    return _read_trackers_indexers_file(config, 'trackers')


def read_indexers_file(config):
    return _read_trackers_indexers_file(config, 'indexers')


def _read_trackers_indexers_file(config, type_: str):
    yaml_filepath = None
    if type_ == 'indexers':
        yaml_filepath = config.get('indexers', 'indexer_file')
    elif type_ == 'trackers':
        yaml_filepath = config.get('trackers', 'tracker_file')
    else:
        raise ValueError("Type_ argument must be indexers or trackers (%s)" % type_)

    output = {}
    try:
        with open(yaml_filepath, 'r') as ymlfile:
            output = yaml.safe_load(ymlfile).get(type_)
    except FileNotFoundError:
        pass
    return output
