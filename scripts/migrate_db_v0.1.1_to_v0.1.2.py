import peewee
from playhouse.migrate import *
from mediastrends.database.peewee.PIMDBObject import PIMDBObject
from mediastrends import db_factory


def main():
    db = db_factory.get_instance()
    migrator = SqliteMigrator(db)

    genres = TextField(null=True)
    language_codes = TextField(null=True)

    with db:
        migrate(
            migrator.add_column('pimdbobject', 'genres', genres),
            migrator.add_column('pimdbobject', 'language_codes', language_codes),
        )

if __name__ == '__main__':
    main()
