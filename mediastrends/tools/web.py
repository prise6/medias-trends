import logging
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import torrent_parser as tp

logger = logging.getLogger(__name__)


def get_request_(url: str, headers):
    with requests.get(url, headers=headers) as response:
        logger.debug('--> status code: %s' % (str(response.status_code)))
        if not response.status_code == requests.codes.ok:
            return None
        else:
            response.raise_for_status()
    return response


def get_request_text(url: str, headers):
    return get_request_(url, headers).text


def get_request_content(url: str, headers):
    return get_request_(url, headers).content


def quote_url(url: str):
    url = urllib.parse.urlsplit(url)
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)

    return url


def parsed_html_content(url, headers):
    html = get_request_text(url, headers)
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def parsed_html_content_from_file(file):
    with open(file, 'r') as f:
        return BeautifulSoup(f.read(), 'html.parser')


def parse_size(size_str: str):
    units = {"o": 1, "ko": 10**3, "mo": 10**6, "go": 10**9, "to": 10**12}

    if len(size_str) <= 1:
        raise ValueError("Cannot parse %s size into int" % size_str)

    size_str = size_str.lower()

    unit = size_str[-2:]
    if unit in units.keys():
        number = size_str[:-2]
    else:
        unit = size_str[-1:]
        if unit == 'o':
            number = size_str[:-1]
        else:
            raise ValueError("Cannot parse %s size into int" % size_str)

    return int(float(number) * units[unit])


def batch(iterable, n=1):
    length = len(iterable)
    for ndx in range(0, length, n):
        yield iterable[ndx:min(ndx + n, length)]


def parse_bencode_tracker(endpoint: str, content: str):
    if endpoint not in ['announce', 'scrape']:
        raise ValueError("Endpoint %s not in default" % (endpoint))

    res = None

    if endpoint == 'announce':
        res = tp.decode(content, hash_fields={'peers': (6, False)})
    elif endpoint == 'scrape':
        tmp = tp.decode(content, encoding='latin1')
        res = {}
        for info_hash, infos in tmp['files'].items():
            res[info_hash.encode('latin1').hex()] = infos
    return res
