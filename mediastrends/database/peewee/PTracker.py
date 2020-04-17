from peewee import Model, CharField

from mediastrends import db_factory


class PTracker(Model):

    name = CharField(max_length=255, unique=True)
    scheme = CharField(max_length=10)
    netloc = CharField(max_length=255)
    path = CharField(max_length=255, null=True)

    class Meta:
        database = db_factory.database_proxy
