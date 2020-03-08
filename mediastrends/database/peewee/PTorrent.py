from peewee import *

from mediastrends import config, db
from .PTracker import PTracker


class PTorrent(Model):

    hash_info = FixedCharField(max_length=40)
    tracker = ForeignKeyField(PTracker)
    name = CharField(max_length=255)
    pub_date = DateTimeField()

    class Meta:
        database = db