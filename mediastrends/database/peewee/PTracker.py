from mediastrends import config, db
from peewee import *


class PTracker(Model):

    name = CharField(max_length=255, unique=True)
    scheme = CharField(max_length=10)
    netloc = CharField(max_length=255)
    path = CharField(max_length=255)

    class Meta:
        database = db