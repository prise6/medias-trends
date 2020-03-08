from peewee import *

from mediastrends import config, db
from .PTracker import PTracker


class PTorrent(Model):

    hash_info = UUIDField(primary_key=True)
    tracker = ForeignKeyField(PTracker)
    name = CharField(max_length=255)
    pub_date = DateTimeField(null = True)
    size = BigIntegerField(null = True)

    class Meta:
        database = db