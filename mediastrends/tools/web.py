import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse

from mediastrends import logger_app, config



def html_content(url: str, headers):
    with requests.get(url, headers=headers) as response:
        logger_app.info('--> status code: %s' % (str(response.status_code)))
        if not response.status_code == requests.codes.ok:
            return None
    return response.text

def quote_url(url: str):
    url = urllib.parse.urlsplit(url)
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)

    return url


def parsed_html_content(url, headers):
    html = html_content(url, headers)
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

