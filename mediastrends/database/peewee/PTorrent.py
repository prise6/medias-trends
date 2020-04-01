from peewee import *

from mediastrends import config, db_factory
from .PTracker import PTracker


class PTorrent(Model):

    STATUS = [(0, 'unfollow'), (1, 'new'), (2, 'follow')]
    CATEGORY = [(0, 'unknown'), (1, 'movie'), (2, 'serie')]

    info_hash = CharField(max_length=40, unique=True)
    name = CharField(max_length=255)
    pub_date = DateTimeField(null = True)
    size = BigIntegerField(null = True)
    status = IntegerField(null = False, default=1, choices=STATUS)
    category = IntegerField(null = False, default=0, choices=CATEGORY)

    class Meta:
        database = db_factory.database_proxy


class PTorrentTracker(Model):

    tracker = ForeignKeyField(PTracker)
    torrent = ForeignKeyField(PTorrent)

    class Meta:
        database = db_factory.database_proxy
        primary_key = CompositeKey('tracker', 'torrent')
