import datetime
import argparse
import os
import logging
from playhouse.sqlite_ext import CSqliteExtDatabase

from mediastrends import config, db_factory
from mediastrends.database.peewee.PTorrent import PTorrent, PTorrentTracker
from mediastrends.database.peewee.PTracker import PTracker
from mediastrends.database.peewee.PPage import PPage
from mediastrends.database.peewee.PStats import PStats
from mediastrends.database.peewee.PTrends import PTrends


logger = logging.getLogger(__name__)

_TABLES_MODELS = {
    'torrent': PTorrent,
    'torrenttracker': PTorrentTracker,
    'tracker': PTracker,
    'page': PPage,
    'stats': PStats,
    'trends': PTrends,
}

_BACKUP_FORMAT = "backup-sqlite-%s.db"
_BACKUP_DATE_FORMAT = "%Y%m%d-%H%M"


def reset_table_(model_name, no_backup, test, **kwargs):
    assert model_name in _TABLES_MODELS.keys()

    if no_backup:
        logger.debug("Not implemented yey")
        return

    model = _TABLES_MODELS.get(model_name, None)
    if test:
        logger.debug("reset_table_ task")
        return
    with db_factory.get_instance():
        model.drop_table()
        model.create_table()


def reset_tables(tables, **kwargs):
    for model_name in tables:
        reset_table_(model_name, **kwargs)


def reset_database(test, no_backup=False, **kwargs):
    if test:
        logger.debug("reset_database task")
        return

    if no_backup:
        logger.warning("No way you don't backup")
        return
    else:
        sqlite_backup(test)
    models = [v for v in _TABLES_MODELS.values()]
    with db_factory.get_instance() as db:
        db.drop_tables(models, safe=True)
        db.create_tables(models)


def sqlite_backup(test, **kwargs):
    if test:
        logger.debug("sqlite_backup task")
        return
    with db_factory.get_instance() as db:
        assert isinstance(db, CSqliteExtDatabase)
        filename = os.path.join(config.get('sqlite', 'backup_dir'), _BACKUP_FORMAT % (datetime.datetime.now().strftime(_BACKUP_DATE_FORMAT)))
        db.backup_to_file(filename)


def load_sqlite_backup(backup_date: str, test, **kwargs):
    if test:
        logger.debug("load_sqlite_backup task")
        return
    with db_factory.get_instance() as db:
        assert isinstance(db, CSqliteExtDatabase)
        backup_filename = os.path.join(config.get('sqlite', 'backup_dir'), _BACKUP_FORMAT % (backup_date))
        db_backup = CSqliteExtDatabase(backup_filename)
        db_backup.backup(db)


def backup_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y%m%d-%H%M").strftime(_BACKUP_DATE_FORMAT)
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)
