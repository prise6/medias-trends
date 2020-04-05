from playhouse.sqlite_ext import CSqliteExtDatabase
from peewee import DatabaseProxy


class PDatabaseFactory:

    def __init__(self, config):
        self.cfg = config
        self.instances = {}
        self.defaut_instance = self.cfg.get('db', 'database')
        self.database_proxy = DatabaseProxy()

    def get_instance(self, instance: str = None):
        if not instance:
            instance = self.defaut_instance
        if instance not in self.instances.keys():
            if instance == 'sqlite':
                instance_obj = CSqliteExtDatabase(self.cfg.get('sqlite', 'path'))
            elif instance == 'memory':
                instance_obj = CSqliteExtDatabase(':memory:')
            else:
                raise ValueError("Instance %s not defined" % (instance))
            self.instances[instance] = instance_obj

        instance = self.instances[instance]
        self.database_proxy.initialize(instance)

        return instance
