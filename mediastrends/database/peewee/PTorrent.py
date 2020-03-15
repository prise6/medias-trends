from peewee import *

from mediastrends import config, db
from .PTracker import PTracker


class PTorrent(Model):

    STATUS = [(0, 'unfollow'), (1, 'new'), (2, 'follow')]

    info_hash = CharField(max_length=40, unique=True)
    name = CharField(max_length=255)
    pub_date = DateTimeField(null = True)
    size = BigIntegerField(null = True)
    status = IntegerField(null = False, default=1, choices=STATUS)

    class Meta:
        database = db


class PTorrentTracker(Model):

    tracker = ForeignKeyField(PTracker)
    torrent = ForeignKeyField(PTorrent)

    class Meta:
        database = db
        primary_key = CompositeKey('tracker', 'torrent')
