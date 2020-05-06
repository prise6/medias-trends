import os
from mediastrends import config, indexers_config, trackers_config, db_factory
from mediastrends.database.peewee.PDbManager import PDbManager
import torrent_parser as tp
import requests
import mediastrends.tools as tools
import mediastrends.tools.torrentfile as tools_tf
from mediastrends.torrent.Tracker import UdpTracker, HttpTracker, tracker_from_url, tracker_from_config_by_name
import pandas as pd
import socket
import struct
import random
import hashlib
import bencode
import logging
import yaml
from unittest.mock import patch, Mock, MagicMock
import base64
from imdb import IMDb, IMDbError
import urllib.error
import PTN



print(PTN.parse("Star Wars : Episode VII - Le Réveil de la Force MULTi 4K ULTRA HD x265"))

exit()
ia = IMDb()
to_search = 'pirates of the caribbean'
results = ia.search_movie(to_search)
# print(ia.get_movie_infoset())
# exit()
movie = results[0]
print(movie.movieID)
print(movie.current_info)
# exit()
# ia.get_movie_vote_details()

print(movie)
print(movie['full-size cover url'])
# print(results[0]['akas'])
# print(results[0]['alternate versions'])
# print(results[0]['vote details'])
exit()
# tmp = base64.b32decode('XFIGXD3FPDXQN6JJLGJVW5DAASZ2TOHG')
tmp = base64.b32decode('XFIGXD3FPDXQN6JJLGJVW5DAASZ2TOH')
tmp = tmp.hex()
print(tmp)

exit()
logging.basicConfig(level="DEBUG")
url = "http://172.24.0.2:9117/dl/yggtorrent/?jackett_apikey=af8xm4bmolqx2agmvhk0gnifwh7vl3p8&path=Q2ZESjhLRTZGRkwzLWhWTHR3Y3V2XzV2dURhaXczU1NxaEMyV2NDNXpMdnVuUktCNlpBNzc0UjBZRmI1QmdnSy11SkxTNE9lOVZOX1ZDVjVQbzRiMGhKdHlvYzFmU1VVUTNBVzdMSll3dVBjN1JRSnN4RzMtVEpzS01zV0M0SDAyejRobWYzNmVaWWE5aTR5bTFCeG9hZnV4cUo0cHlyOElRem92dEV1ZzY5azZxNHFzcXpfa0pwcldtaXgwOW1sSjRnWGRn&file=Press.S01.VOSTFR.720p.HDTV.x264-Akebono"
# test = "Q2ZESjhLRTZGRkwzLWhWTHR3Y3V2XzV2dURaY2V1ZjViZ2RHeFpvTnNRWkJtWUwtanV4UjlwR1RPR0VLdl9XSXdlX2JEdU12Y2Q2cW82Z1JpeHIxNnpPXzlHTEFMOVV3Vjdoa01ZbWVqTlN2Yzk1el9uZE9RQUNJOUE3WFpwZWcwTGQyT3FkVEwyTFpqSi1xX0x2eDZXcHR2WldOVENhN2VodFZULVFMUUhSMXNGOWx1eXZRbGJVc0F2YUlLRzM5T1dsaFpYNFNCenFPbWJZeHh4Y0RyZG5IR0Jv"
test = "Q2ZESjhLRTZGRkwzLWhWTHR3Y3V2XzV2dURhaXczU1NxaEMyV2NDNXpMdnVuUktCNlpBNzc0UjBZRmI1QmdnSy11SkxTNE9lOVZOX1ZDVjVQbzRiMGhKdHlvYzFmU1VVUTNBVzdMSll3dVBjN1JRSnN4RzMtVEpzS01zV0M0SDAyejRobWYzNmVaWWE5aTR5bTFCeG9hZnV4cUo0cHlyOElRem92dEV1ZzY5azZxNHFzcXpfa0pwcldtaXgwOW1sSjRnWGRn"
# test = "eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImV4cGlyZXMiOjEyNzk3NDYwMDAsIm9hdXRoX3Rva2VuIjoiMjk1NjY2Njk1MDY0fDIuRXpwem5IRVhZWkJVZmhGQ2l4ZzYzUV9fLjM2MDAuMTI3OTc0NjAwMC0xMDAwMDA0ODMyNzI5MjN8LXJ6U1pnRVBJTktaYnJnX1VNUUNhRzlNdEY4LiIsInVzZXJfaWQiOiIxMDAwMDA0ODMyNzI5MjMifQ"
# test = "Q2ZESjhNcnVtalc0c0NaRm1Nb0J6VVp0YmZUSEJEaVJQMUFyMXI2YUtmYmNIM1FXWEZTQUZTRUVXVHZ5N0dYSFNCV0JrQlBkYnoyS2N0czhNUE02Z0FZelRsZlVZWFhnNXBOUERoQjFoSUY4QllRcF9nb1gtalNha1o3VlYxTFFhTi1PTm1VSFlWZ005akkwWm1TSzM5OFdJc0lhZVJKVmt6RUJFdWRIQkYyRkRrM2ZqaWR3QmppOGlxNDNpeER3bWVVbDJ2bWdMR0YyWnJQenh5blZkNTl4QTl5OHVJVTZic0QyanFWMDljTGUwaEhNZzJjUFhUN0hHZDZ5bVJaVzM3NlpobGdCMW9DamdPa2lETDlzWW80STNvUjVVTGRpZXlZVWVkbDIwWTgwMVZnVmNlMGw4WEJDV1NkRVJrMGhiSFMyMDNpR1hFbExhMnBKVzl4Q1lRdU1kNFJDVEUxWlZQRzlEQmNraG9PbENxdWZfWnBmQUtRNmZLT0IyN1RfMWhaejFrUzNiOWZfdm5aMTJrdUNnRVl5VmVFel9hMUZhZnJHRHN6SHVoYXdhdFJDSVEzTDBqOFZfWWpUSlpHSFNLRWhCc0E0R1FoWmx1WFZ3bmNLQjVVMUloYWlUNWVnY1NsRWN1OTZFQWc2VnJpN0R3blRwVGVfQllBdVo0TGdjeUZNSGpMNW9mbkwxUGZmRm5PZmZmUHRUbDQ"
test = "Q2ZE"
res = base64.b64decode(test)
# res = base64.urlsafe_b64decode(test)
# res = res.decode('utf-8')
# res = test.encode('base64')

print(res)
exit()
db = db_factory.get_instance()
db.connect()
db.close()
print(db.is_closed())
print(db.is_closed())

tr = PDbManager.get_tracker_by_name('ygg')
print(tr)


exit()
info_hashes = ["85be94b120becfb44f94f97779c61633c7647629", "3ECC03A3E3695AEBEFD1DCB2F652ADF8E6336346", "b30af856e4fcd4328a70d4bdc2dc6315edcca925"]

tr = tracker_from_config_by_name('yts-opentrackr')
res = tr.scrape(info_hashes)
print(res)
res = tr.scrape(info_hashes)
print(res)
exit()
class Class():
    def __init__(self):
        self.param = None

    def method(self):
        pass

with patch('__main__.Class') as MockClass:
    instance = MockClass.return_value
    instance.method.return_value = 'foo'
    assert Class() is instance
    print(MockClass.called)
    assert Class().method() == 'foo'


with patch("mediastrends.torznab.TorznabRSS.TorznabJackettRSS") as MockClass:
    instance = MockClass.return_value
    # print(instance)
    # instance.process_items = MagicMock(return_value = "ici")
    instance.ok = 'lol'
    instance.process_items.return_value = "ici"
    instance.parse.return_value = True
    from mediastrends.torznab.TorznabRSS import TorznabJackettRSS

    # print(TorznabJackettRSS("ok").process_items())
    o = TorznabJackettRSS("ok")
    print(MockClass.called)
    # exit()
    print(o.ok)
    print(o.parse())
    print(o.process_items())
    


exit()
static_content = ['ici']

class Test():

    def __init__(self, content= static_content):
        self.content = content
        self.rd = random.random()

    def __str__(self):
        return self.content[0]

# a = Test()
# print(a)
# static_content[0] = "la"
# print(a)
# exit()

class TestFactory():
    instances = {}
    content = static_content

    @classmethod
    def create(cls, name):
        if name not in cls.instances:
            cls.instances[name] = Test(cls.content)
        return cls.instances[name]


print(TestFactory.create('coucou').rd)
print(TestFactory.create('coucou').rd)
print(TestFactory.create('loool').rd)

print(TestFactory.create('coucou'))
print(TestFactory.create('loool'))

static_content[0] = "B"

print(TestFactory.create('coucou'))
print(TestFactory.create('loool'))
print(TestFactory.create('new'))

exit()
# info_hashes = ["3ECC03A3E3695AEBEFD1DCB2F652ADF8E6336346", "0000090fb27d8dd4e323ba0713a085c908451727"]
info_hashes = ["85be94b120becfb44f94f97779c61633c7647629", "3ECC03A3E3695AEBEFD1DCB2F652ADF8E6336346", "b30af856e4fcd4328a70d4bdc2dc6315edcca925"]

# tracker = tracker_from_url('http://ygg.peer2peer.cc:8080/oYfKNe6xioo2jPnt95sVo9gmQDhwGK4q/scrape', name = "ygg")
# res = tracker.scrape(info_hashes)
# print(tracker._request_obj.content)
# print(res)
# exit()

# tracker = UdpTracker('udp', 'open.stealth.si:80', path = None, name = 'test')
tracker = yts_tracker
res = tracker._headers
print(res)
res = tracker.scrape(info_hashes)
print(res)
res = tracker.scrape(info_hashes)
print(res)
exit()

# info_hash = "0000090fb27d8dd4e323ba0713a085c908451727"
# print(len(info_hash.decode('hex')))
# print(len(bytes.fromhex(info_hash)))

YTS_TORRENT_NAME = 'Elephant (2020) [720p] [BluRay] [YTS.MX].torrent'
YTS_TORRENT_NAME = '[ gktorrent.io ] The Gentlemen FRENCH WEBRIP 2020.torrent'
YTS_TORRENT_NAME = 'KOH-LANTA.10.04-2020.S21.L’ÎLE DES HÉROS.E07.HDTV.1080i.MKV.AVC.E-AC3.AC3-BB85.mkv.torrent'
YTS_TORRENT_FILENAME = os.path.join(config.get('directory', 'data'), YTS_TORRENT_NAME)
info_hash = "0000090fb27d8dd4e323ba0713a085c908451727"


tracker_url = "udp://tracker.coppersurfer.tk:6969/announce"
info_hash = "3ECC03A3E3695AEBEFD1DCB2F652ADF8E6336346"

# udp://public.popcorn-tracker.org:6969/announce
print("---> Connexion ...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# TRACKER_HOST = "tracker.coppersurfer.tk"
TRACKER_HOST = "public.popcorn-tracker.org"
TRACKER_HOST = "tracker.torrent.eu.org"
# TRACKER_PORT = 6969

TRACKER_HOST = "tracker.opentrackr.org"
TRACKER_PORT = 1337

TRACKER_HOST = "opentor.org"
TRACKER_PORT = 2710

# TRACKER_HOST = "ygg.peer2peer.cc"
# TRACKER_PORT = 8080

# TRACKER_HOST = "open.stealth.si"
# TRACKER_PORT = 80

CONNECTION_ID = 0x41727101980
sock.connect((TRACKER_HOST, TRACKER_PORT))
TRANSACTION_ID = random.randint(0, 1 << 32 - 1)
print("TRANSACTION_ID: %s" % TRANSACTION_ID)
print("CONNECTION_ID: %s" % CONNECTION_ID)

print("---> scrape connect ...")
payload = struct.pack('!QII', CONNECTION_ID, 0, TRANSACTION_ID)
sock.sendall(payload)
try:
    sock.settimeout(10)
    response = sock.recv(2048)
    print(response)
except Exception as err:
    print(err)
c = struct.unpack('!IIQ', response)
print(c)

## scrape input
print("---> scrape")
payload = struct.pack('!QII', c[2], 2, TRANSACTION_ID)
payload += bytes.fromhex(info_hash)
sock.sendall(payload)
sock.sendall(payload)
try:
    sock.settimeout(3)
    response = sock.recv(2048)
except Exception as err:
    print(err)
# print(response[:4].decode('utf-8'))
c = struct.unpack('!LL', response[:8])
print(c)
if c[0] ==3:
    print(response[8:].decode('utf-8'))
    print(len(response))
    tmp = response[8:16]
    err = struct.unpack('8p', tmp)
    print(err)
elif c[0] == 2:
    content = struct.unpack('!LLL', response[8:])
    print(content)

sock.close()

## refs:
## https://github.com/sourcepirate/python-udptracker/blob/79e1b9294cffd2f2917d73e71996bd9d702b2945/udptrack/__init__.py#L102
## http://xbtt.sourceforge.net/udp_tracker_protocol.html


