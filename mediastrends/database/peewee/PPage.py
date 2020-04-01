from peewee import *

from mediastrends import config, db_factory
from .PTorrent import PTorrent
from .PTracker import PTracker

class PPage(Model):

    torrent = ForeignKeyField(PTorrent)
    tracker = ForeignKeyField(PTracker)
    url = CharField(max_length=2048)

    class Meta:
        database = db_factory.database_proxy
        primary_key = CompositeKey('torrent', 'tracker')