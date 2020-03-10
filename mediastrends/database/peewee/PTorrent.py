from peewee import *

from mediastrends import config, db
from .PTracker import PTracker


class PTorrent(Model):

    info_hash = CharField(max_length=40, unique=True)
    name = CharField(max_length=255)
    pub_date = DateTimeField(null = True)
    size = BigIntegerField(null = True)

    class Meta:
        database = db


class PTorrentTracker(Model):

    tracker = ForeignKeyField(PTracker)
    torrent = ForeignKeyField(PTorrent)

    class Meta:
        database = db
        primary_key = CompositeKey('tracker', 'torrent')
