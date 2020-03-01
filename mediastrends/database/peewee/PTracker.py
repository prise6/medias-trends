from mediastrends import config, db
from peewee import *


class PTracker(Model):

    name = CharField(max_length=255, unique=True)
    url = CharField(max_length=255)

    class Meta:
        database = db