import os
from playhouse.sqlite_ext import CSqliteExtDatabase
from peewee import DatabaseProxy


class PDatabaseFactory:

    def __init__(self, config):
        self.cfg = config
        self.instances = {}
        self.defaut_instance = self.cfg.get('db', 'database')
        self.sqlite_db_path = self.cfg.get('sqlite', 'path')
        self.database_proxy = DatabaseProxy()

    def get_instance(self, instance: str = None):
        if not instance:
            instance = self.defaut_instance
        if instance not in self.instances.keys():
            if instance == 'sqlite':
                instance_obj = CSqliteExtDatabase(self.sqlite_db_path)
            elif instance == 'sqlite-app-test':
                PACKAGR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                instance_obj = CSqliteExtDatabase(os.path.join(PACKAGR_DIR, 'mediastrends_test.db'))
            elif instance == 'memory':
                instance_obj = CSqliteExtDatabase(':memory:')
            else:
                raise ValueError("Instance %s not defined" % (instance))
            self.instances[instance] = instance_obj

        instance = self.instances[instance]
        self.database_proxy.initialize(instance)

        return instance
