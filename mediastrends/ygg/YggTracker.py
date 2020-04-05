from mediastrends import config
from mediastrends.torrent.Tracker import Tracker

ygg_tracker = Tracker(
    scheme=config.get('ygg', 'scheme'),
    netloc=config.get('ygg', 'netloc'),
    path=config.get('ygg', 'path'),
    name='ygg'
)
