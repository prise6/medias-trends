import datetime

class Torrent:
    
    def __init__(self, info_hash: str, name: str, pub_date: datetime.date, size: int):
        self._info_hash = info_hash
        self._name = name
        self._pub_date = pub_date
        self._size = size

    @property
    def info_hash(self):
        return self._info_hash

    @property
    def name(self):
        return self._name

    @property
    def pub_date(self):
        return self._pub_date

    @property
    def size(self):
        return self._size
        
