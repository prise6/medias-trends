from peewee import *

from mediastrends import config, db
from .PTorrent import PTorrent
from .PTracker import PTracker


class PStats(Model):

    torrent = ForeignKeyField(PTorrent)
    tracker = ForeignKeyField(PTracker)
    leechers = IntegerField()
    seeders = IntegerField()
    completed = IntegerField(null=True)
    valid_date = DateTimeField()

    class Meta:
        database = db

