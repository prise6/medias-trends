from peewee import *

from mediastrends import config, db
from .PTorrent import PTorrent

class PPage(Model):

    torrent = ForeignKeyField(PTorrent, unique = True)
    url = CharField(max_length=2048)

    class Meta:
        database = db