import datetime
import time
import os
from playhouse.sqlite_ext import CSqliteExtDatabase
from mediastrends import config, db_factory
from mediastrends.database.peewee.PTorrent import PTorrent, PTorrentTracker 
from mediastrends.database.peewee.PTracker import PTracker
from mediastrends.database.peewee.PPage import PPage
from mediastrends.database.peewee.PStats import PStats
from mediastrends.database.peewee.PTrends import PTrends


_TABLES_MODELS = {
    'torrent': PTorrent,
    'torrenttracker': PTorrentTracker,
    'tracker': PTracker,
    'page': PPage,
    'stats': PStats,
    'trends': PTrends,
}

_BACKUP_FORMAT = "backup-sqlite-%s.db"
_BACKUP_DATE_FORMAT = "%Y%m%d"

def reset_table_(model_name):
    assert model_name in _TABLES_MODELS.keys()
    
    model = _TABLES_MODELS.get(model_name, None)
    with db_factory.get_instance() as db:
        model.drop_table()
        model.create_table()

def reset_database(backup = True):
    if backup:
        sqlite_backup()
    models = [v for v in _TABLES_MODELS.values()]
    with db_factory.get_instance() as db:
        db.drop_tables(models, safe=True)
        db.create_tables(models)

def sqlite_backup():
    with db_factory.get_instance() as db:
        assert isinstance(db, CSqliteExtDatabase)
        filename = os.path.join(config.get('sqlite', 'backup_dir'), _BACKUP_FORMAT % (datetime.date.today().strftime(_BACKUP_DATE_FORMAT)))
        db.backup_to_file(filename)

def load_sqlite_backup(valid_date: str):
    with db_factory.get_instance() as db:
        assert isinstance(db, CSqliteExtDatabase)
        backup_filename = os.path.join(config.get('sqlite', 'backup_dir'), _BACKUP_FORMAT % (valid_date))
        db_backup = CSqliteExtDatabase(backup_filename)
        db_backup.backup(db)

def backup_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y%m%d").strftime(_BACKUP_DATE_FORMAT)
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)
