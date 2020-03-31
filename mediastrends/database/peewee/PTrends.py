from peewee import *

from mediastrends import config, db
from .PTorrent import PTorrent
from .PTracker import PTracker


class PTrends(Model):

    torrent = ForeignKeyField(PTorrent)
    valid_date = DateTimeField()
    score = DoubleField()

    class Meta:
        database = db
        indexs = (
            (('torrent', 'valid_date'), True),
        )
