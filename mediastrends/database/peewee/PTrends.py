from peewee import *

from mediastrends import config, db_factory
from .PTorrent import PTorrent
from .PTracker import PTracker


class PTrends(Model):

    torrent = ForeignKeyField(PTorrent)
    valid_date = DateTimeField()
    score = DoubleField()

    class Meta:
        database = db_factory.database_proxy
        indexes = (
            (('torrent', 'valid_date'), True),
        )
