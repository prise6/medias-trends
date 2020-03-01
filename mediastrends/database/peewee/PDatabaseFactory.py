from peewee import SqliteDatabase


class PDatabaseFactory:

    def __init__(self, config):
        self.cfg = config
        self.instances = {}

    def get_instance(self, instance: str):
        if instance not in self.instances.keys():
            if instance == 'sqlite':
                instance_obj = SqliteDatabase(self.cfg.get('sqlite', 'path'))
                self.instances[instance] = instance_obj
            else:
                raise ValueError("Instance %s n'est pas définie" % (instance))
        return self.instances[instance]