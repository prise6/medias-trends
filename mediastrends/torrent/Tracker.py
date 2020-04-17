"""
Inspired by
https://github.com/sourcepirate/python-udptracker/blob/79e1b9294cffd2f2917d73e71996bd9d702b2945/udptrack/__init__.py#L102
http://xbtt.sourceforge.net/udp_tracker_protocol.html
"""
import logging
import urllib.parse
import random
import struct
import socket
import requests
from typing import List
from mediastrends import config, trackers_config
import torrent_parser as tp

logger = logging.getLogger(__name__)


class Tracker:

    _ACTIONS = {
        'CONNECT': 0,
        'ANNOUNCE': 1,
        'SCRAPE': 2,
        'ERROR': 3,
    }

    def __init__(self, scheme, netloc, path, name):
        self._scheme = scheme
        self._netloc = netloc
        self._path = path
        self._name = name
        self._headers = {}
        self._response = {'content': None, 'parsed': None}
        self._request = {'action': None, 'params': None, 'payload': None}

    @property
    def scheme(self):
        return self._scheme

    @property
    def netloc(self):
        return self._netloc

    @property
    def path(self):
        return self._path if self._path else ''

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return urllib.parse.urlunsplit(
            urllib.parse.SplitResult(self.scheme, self.netloc, self.path, None, None)
        )

    def build_header(self, action: str = None):
        raise NotImplementedError()

    def build_request(self, action: str = None, params: dict = None):
        raise NotImplementedError()

    def send_request(self):
        raise NotImplementedError()

    def get_response(self):
        raise NotImplementedError()

    def parse_response(self) -> dict:
        raise NotImplementedError()

    def query_tracker(self, action: str = None, params: dict = None):
        self.build_header(action)
        self.build_request(action, params)
        self.send_request()
        self.get_response()
        self.parse_response()

    def scrape(self, info_hashes: List[str]):
        params = {'info_hash': [bytes.fromhex(info_hash) for info_hash in info_hashes]}
        self.query_tracker('SCRAPE', params)
        return self._response['parsed']


class HttpTracker(Tracker):

    def __init__(self, scheme, netloc, path, name):
        super().__init__(scheme, netloc, path, name)
        self._timeout = 10
        self._request_obj = None

    def build_header(self, action: str = None):
        self._headers['user-agent'] = config.get('requests', 'user_agent')

    def build_request(self, action: str = None, params: dict = None):
        if action not in self._ACTIONS:
            raise ValueError('Action %s not supported' % action)
        payload = {}
        if self._ACTIONS[action] == 2:
            assert isinstance(params, dict) and 'info_hash' in params
            payload = params

        self._request = {
            'action': action,
            'params': params,
            'payload': payload
        }

    def send_request(self):
        self._request_obj = requests.get(self.url, params=self._request['payload'], timeout=self._timeout)

    def get_response(self):
        self._response['content'] = self._request_obj.content
        return self._response

    def parse_response(self):
        self._request_obj.raise_for_status()

        content = self._response.get('content')

        if not isinstance(content, bytes):
            raise TypeError('response content must be instance of bytes')

        if self._request['action'] == 'SCRAPE':
            tmp = tp.decode(content, encoding='latin1')
            self._response['parsed'] = {}
            for info_hash, infos in tmp['files'].items():
                self._response['parsed'][info_hash.encode('latin1').hex()] = infos

        return self._response['parsed']


class UdpTracker(Tracker):

    def __init__(self, scheme, netloc, path, name):
        super().__init__(scheme, netloc, path, name)
        self._timeout = 10
        self._sock = None

    def build_header(self, action: str = None):
        self._headers['transaction_id'] = random.randint(0, 1 << 32 - 1)
        if self._ACTIONS[action] == 0:
            self._headers['connection_id'] = 0x41727101980

    def build_request(self, action: str = None, params: dict = None):
        if action not in self._ACTIONS:
            raise ValueError('Action %s not supported' % action)
        headers_payload = struct.pack('!QII', self._headers['connection_id'], self._ACTIONS[action], self._headers['transaction_id'])
        payload = headers_payload
        if self._ACTIONS[action] == 2:
            payload += b''.join(params['info_hash'])
        if self._ACTIONS[action] == 0:
            # use params to pass host and port
            params = self.netloc.split(':')
            params[1] = int(params[1])
            params = tuple(params)
            # create socket
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._request = {
            'payload': payload,
            'action': action,
            'params': params
        }

    def send_request(self):
        # check if request require socket connexion
        if self._request['action'] == 'CONNECT':
            self._sock.connect(self._request['params'])
        self._sock.sendall(self._request['payload'])

    def get_response(self):
        self._sock.settimeout(self._timeout)
        try:
            self._response['content'] = self._sock.recv(2048)
        except socket.timeout as err:
            logger.warning('Socket request timeout')
            raise err
        return self._response

    def parse_response(self):
        if not isinstance(self._response.get('content'), bytes):
            raise TypeError('response must be instance of bytes')

        headers = self._response.get('content')[:8]
        payload = self._response.get('content')[8:]

        action, transaction_id = struct.unpack('!II', headers)

        assert transaction_id == self._headers['transaction_id']

        if action == self._ACTIONS['CONNECT']:
            connection_id = struct.unpack('!Q', payload)[0]
            self._headers['connection_id'] = connection_id

        if action == self._ACTIONS['ERROR']:
            error_content = payload.decode('utf-8')
            raise ValueError(error_content)

        if action == self._ACTIONS['SCRAPE']:
            info_struct = '!LLL'
            info_size = struct.calcsize(info_struct)
            info_count = len(payload) // info_size
            info_hashes = [info_hash.hex() for info_hash in self._request['params']['info_hash']]

            assert len(info_hashes) == info_count

            self._response['parsed'] = {}
            for info_offset in range(info_count):
                offset = info_size * info_offset
                info = payload[offset:(offset + info_size)]
                seeders, completed, leechers = struct.unpack(info_struct, info)
                self._response['parsed'][info_hashes[info_offset]] = {
                    'complete': seeders,
                    'downloaded': completed,
                    'incomplete': leechers
                }

        return self._response['parsed']

    def scrape(self, info_hashes: List[str]):
        self.query_tracker('CONNECT')
        parsed_reponse = super().scrape(info_hashes)
        self._sock.close()
        return parsed_reponse


#
# class instanciation
#

def tracker_from_url(url, name: str) -> Tracker:
    if not isinstance(url, urllib.parse.SplitResult):
        url = urllib.parse.urlsplit(url)
    _cls = Tracker
    if url[0] in ['http', 'https']:
        _cls = HttpTracker
    if url[0] in ['udp']:
        _cls = UdpTracker

    return _cls(url[0], url[1], url[2], name)


def tracker_from_config_by_name(name: str) -> Tracker:
    if name in trackers_config:
        return tracker_from_url(urllib.parse.SplitResult(
            trackers_config.get(name).get('scheme'),
            trackers_config.get(name).get('netloc'),
            trackers_config.get(name).get('path'),
            None,
            None,
        ), name)
    return None


def tracker_from_config_by_url(url: str) -> Tracker:
    tracker = tracker_from_url(url, "tbd")
    for name, infos in trackers_config.items():
        if infos.get('active', False) and infos.get('scheme') == tracker.scheme and infos.get('netloc') == tracker.netloc:
            tracker._name = name
            return tracker
    return None
