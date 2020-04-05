from peewee import Model, DoubleField, DateTimeField, ForeignKeyField

from mediastrends import db_factory
from .PTorrent import PTorrent


class PTrends(Model):

    torrent = ForeignKeyField(PTorrent)
    valid_date = DateTimeField()
    score = DoubleField()

    class Meta:
        database = db_factory.database_proxy
        indexes = (
            (('torrent', 'valid_date'), True),
        )
