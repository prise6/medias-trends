import datetime
import logging
from typing import Union
from mediastrends import STATUS_NAME, CATEGORY_NAME
import mediastrends.tools.torrentfile as tools_tf

logger = logging.getLogger(__name__)


class Torrent:

    _CAT_UNKNOWN = CATEGORY_NAME['unknown']
    _CAT_MOVIE = CATEGORY_NAME['movies']
    _CAT_SERIE = CATEGORY_NAME['series']

    _STATUS_UNFOLLOW = STATUS_NAME['unfollow']
    _STATUS_NEW = STATUS_NAME['new']
    _STATUS_FOLLOW = STATUS_NAME['follow']

    def __init__(self, info_hash: str, name: str, pub_date: datetime.datetime, size: int, status: int = _STATUS_NEW, category: int = _CAT_UNKNOWN):
        self.info_hash = info_hash
        self.name = name
        self.pub_date = pub_date
        self.size = size
        self._status = status
        self._category = category
        self._imdb_id = None

    @property
    def info_hash(self):
        return self._info_hash

    @info_hash.setter
    def info_hash(self, info_hash: str):
        if isinstance(info_hash, str) and len(info_hash) == 40 and int(info_hash, 16):
            self._info_hash = info_hash.lower()
        else:
            raise ValueError('Info hash must be hexadecimal string (%s)' % info_hash)

    @property
    def name(self: str):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, str):
            self._name = name
        else:
            raise TypeError('Torrent name must be a string (%s)' % name)

    @property
    def pub_date(self):
        return self._pub_date

    @pub_date.setter
    def pub_date(self, pub_date: datetime.datetime):
        if isinstance(pub_date, datetime.datetime):
            self._pub_date = pub_date
        else:
            raise TypeError('Torrent publish date must be a datetime object (%s)' % pub_date)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        if isinstance(size, int):
            self._size = size
        else:
            raise TypeError('Torrent size must be an integer (%s)' % size)

    @property
    def status(self):
        return self._status

    @property
    def category(self):
        return self._category

    @property
    def imdb_id(self):
        return self._imdb_id

    @imdb_id.setter
    def imdb_id(self, imdb_id: str):
        if imdb_id and not isinstance(imdb_id, str):
            raise ValueError("Imdb id must instance of string if not None")
        self._imdb_id = imdb_id
        return self

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
        return "%s: %s (%s/%s)" % (
            self._info_hash,
            self._name,
            self._pub_date,
            self._category
        )


class TorrentFile(Torrent):

    def __init__(self, resource, **kwargs):
        self.resource = resource
        self._content = None
        self._extras = {}
        self.populate_torrent_arguments(kwargs)

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, resource):
        if resource is None:
            raise ValueError("Resource cannot be None")
        self._resource = resource
        return self

    @property
    def content(self):
        if not self._content:
            self.content = tools_tf.read_resource(self.resource)
        return self._content

    @content.setter
    def content(self, content: Union[bytes, str]):
        if isinstance(content, bytes) | isinstance(content, str):
            self._content = content
        else:
            raise TypeError("File Torrent content must be instance of bytes or string")
        return self

    @property
    def extras(self):
        if not self._extras:
            logger.debug('Parsing torrent file to get extras infos...')
            self.extras = tools_tf.parse(self.content)
        return self._extras

    @extras.setter
    def extras(self, extras: dict):
        if not isinstance(extras, dict):
            raise TypeError("Extras attribute must be dict instance")
        self._extras = extras
        return self

    def populate_torrent_arguments(self, torrents_args):
        if not torrents_args.get('info_hash'):
            torrents_args['info_hash'] = self.extras.get('info_hash')

        if not torrents_args.get('name'):
            torrents_args['name'] = self.extras.get('name')

        if not torrents_args.get('pub_date'):
            torrents_args['pub_date'] = self.extras.get('creation_date')

        if not torrents_args.get('size'):
            torrents_args['size'] = self.extras.get('length')

        return super().__init__(**torrents_args)

    def __getattr__(self, attr):
        return self.extras.get(attr, None)
