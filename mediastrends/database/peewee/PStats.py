from peewee import Model, ForeignKeyField, IntegerField, DateTimeField

from mediastrends import db_factory
from .PTorrent import PTorrent
from .PTracker import PTracker


class PStats(Model):

    torrent = ForeignKeyField(PTorrent, backref='stats')
    tracker = ForeignKeyField(PTracker)
    leechers = IntegerField()
    seeders = IntegerField()
    completed = IntegerField(null=True)
    valid_date = DateTimeField()

    class Meta:
        database = db_factory.database_proxy
