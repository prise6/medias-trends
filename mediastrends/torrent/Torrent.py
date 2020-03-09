import datetime

class Torrent:
    
    def __init__(self, hash_info: str, name: str, pub_date: datetime.date, size: int):
        self._hash_info = hash_info
        self._name = name
        self._pub_date = pub_date
        self._size = size

    @property
    def hash_info(self):
        return self._hash_info

    @property
    def name(self):
        return self._name

    @property
    def pub_date(self):
        return self._pub_date

    @property
    def size(self):
        return self._size
        
