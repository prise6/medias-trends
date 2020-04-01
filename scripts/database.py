import argparse
import datetime
from mediastrends.tasks import *


def main(action, table_names: list = None, backup_date: str = None):

    if action == 'reset_db':
        reset_database()
    elif action == 'reset_table':
        for table_name in tables_names:
            reset_table_(table_name)
    elif action == 'backup_db':
        sqlite_backup()
    elif action == 'load_backup':
        load_sqlite_backup(backup_date)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="Action on database", type=str, choices = ["reset_db", "reset_table", "backup_db", "load_backup"])
    parser.add_argument("-t", "--tables", help="Tables names", type=str, nargs = '+', choices = ["torrent", "torrentracker", "tracker", "page", "stats", "trends"])
    parser.add_argument("-d", "--backup_date", help="Backup date: YYYYMMDD", type=backup_date)

    args = parser.parse_args()
    main(args.action, args.tables, args.backup_date)
    exit()



