from peewee import *

from mediastrends import config, db
from .PTracker import PTracker


class PTorrent(Model):

    hash = FixedCharField(max_length=40)
    tracker = ForeignKeyField(PTracker)
    title = CharField(max_length=255)
    add_date = DateField()

    class Meta:
        database = db