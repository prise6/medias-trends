from peewee import Model, CharField, FloatField, IntegerField, TextField
from mediastrends import db_factory


class PIMDBObject(Model):
    imdb_id = CharField(max_length=15, primary_key=True)
    title = TextField(null=False)
    rating = FloatField(null=True)
    year = IntegerField(null=True)
    cover_url = TextField(null=True)
    genres = TextField(null=True)
    language_codes = TextField(null=True)

    class Meta:
        database = db_factory.database_proxy
