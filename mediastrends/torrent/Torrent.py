import datetime


class Torrent:

    _CAT_UNKNOWN = 0
    _CAT_MOVIE = 1
    _CAT_SERIE = 2

    _STATUS_UNFOLLOW = 0
    _STATUS_NEW = 1
    _STATUS_FOLLOW = 2

    def __init__(self, info_hash: str, name: str, pub_date: datetime.date, size: int, status: int = 1, category: int = 0):
        self._info_hash = info_hash
        self._name = name
        self._pub_date = pub_date
        self._size = size
        self._status = status
        self._category = category

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

    @property
    def status(self):
        return self._status

    @property
    def category(self):
        return self._category

    def follow(self):
        self._status = 2
        return self

    def new(self):
        self._status = 1
        return self

    def unfollow(self):
        self._status = 0
        return self

    def __str__(self):
        return "%s: %s (%s)" % (
            self._info_hash,
            self._name,
            self._pub_date
        )
