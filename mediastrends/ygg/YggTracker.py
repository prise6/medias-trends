"""
DEPRECATED : use of Jackett + Torznab specification
"""

from mediastrends import config
from mediastrends.torrent.Tracker import HttpTracker

ygg_tracker = HttpTracker(
    scheme=config.get('ygg', 'scheme'),
    netloc=config.get('ygg', 'netloc'),
    path=config.get('ygg', 'path'),
    name='ygg'
)
