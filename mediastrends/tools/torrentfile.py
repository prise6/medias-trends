"""
General tool functions about torrentfile
"""
from typing import Union
import hashlib
import bencode
import requests
import urllib.parse
import datetime
import re
import base64

from mediastrends import config


def parse(content: Union[bytes, str]) -> dict:
    if isinstance(content, bytes):
        return parse_bytes(content)
    if isinstance(content, str):
        return parse_str(content)


def parse_str(content: str):
    """Parse content of string content.
    Only magnet link correspond.

    Args:
        content (str): String content (magnet link only)

    Returns:
        dict: with following keys

            * 'info_hash': str (hexadecimal values),
            * 'tracker_urls': list
    Raises:
        NotImplementedError: If content corresponds not to magnet link
    """
    if content.startswith('magnet:'):
        url_parse = urllib.parse.urlparse(content)
        params = urllib.parse.parse_qs(url_parse.query)

        if 'xt' not in params:
            raise ValueError("Magnet link must have xt param")
        if 'tr' not in params:
            raise ValueError("Magnet link must have tr param")

        xt_param = params.get('xt')[0]
        match = re.search(r'urn:btih:([0-9A-Za-z]+)', xt_param)
        candidate_info_hash = match.group(1) if match else None

        if not candidate_info_hash:
            raise ValueError("No info hash candidates")

        info_hash = None
        if len(candidate_info_hash) == 40 and int(candidate_info_hash, 16):
            info_hash = candidate_info_hash
        elif len(candidate_info_hash) == 32:
            try:
                info_hash = base64.b32decode(candidate_info_hash).hex()
            except Exception:
                pass

        if not info_hash:
            raise ValueError("Info hash in magnet does not match hexadecimal or base32")

        tracker_urls = [extract_tracker_url_from_announce(url) for url in params.get('tr')]
        tracker_urls = [url_split for url_split in tracker_urls if url_split.scheme and url_split.netloc]

        res = {
            'info_hash': info_hash,
            'tracker_urls': tracker_urls
        }
        return res
    raise NotImplementedError


def parse_bytes(content: bytes) -> dict:
    """Parse only needed values by this app
    from content of torrent file (.torrent)

    See: https://wiki.theory.org/index.php/BitTorrentSpecification#Metainfo_File_Structure

    Args:
        content (bytes): binary content of torrent file

    Returns:
        dict: with following keys

            * 'name': str
            * 'info_hash': str (hexadecimal values),
            * 'tracker_urls': list
            * 'creation_date': datetime.datetime
            * 'length': integer, number of bytes with 1024 convention (for kilo,...)
    """
    decoded_content = bencode.decode(content)

    return_dict = {}

    return_dict['name'] = decoded_content['info']['name']
    return_dict['info_hash'] = hashlib.sha1(bencode.encode(decoded_content['info'])).hexdigest()

    announce_list = []
    announce_list.append(decoded_content.get('announce'))

    if "announce-list" in decoded_content:
        announce_list.extend([url for urls in decoded_content.get('announce-list') for url in urls])

    tracker_urls = [extract_tracker_url_from_announce(url) for url in announce_list if url]
    tracker_urls = [url_split for url_split in tracker_urls if url_split.scheme and url_split.netloc]
    return_dict['tracker_urls'] = tracker_urls

    if "creation date" in decoded_content:
        return_dict['creation_date'] = datetime.datetime.fromtimestamp(int(decoded_content['creation date']))

    if "length" in decoded_content['info']:
        return_dict['size'] = int(decoded_content['info']['length'])

    if "files" in decoded_content['info']:
        for file_info in decoded_content['info']['files']:
            if "length" in file_info:
                if 'size' in return_dict:
                    return_dict['size'] += int(file_info['length'])
                else:
                    return_dict['size'] = int(file_info['length'])

    return return_dict


def read_from_url(url: str, headers: dict = {}) -> bytes:
    """Binary response content from torrent file url

    Args:
        url (str): url of torrent file
        headers (dict, optional): key value pair of headers. Defaults to None.

    Returns:
        bytes: binary response content
    """
    if 'user-agent' not in headers:
        headers['user-agent'] = config.get('requests', 'user_agent')

    try:
        with requests.get(url, headers=headers) as req:
            req.raise_for_status()
    except requests.exceptions.InvalidSchema:
        with requests.get(url, headers=headers, allow_redirects=False) as req:
            if req.headers.get('Location') and req.headers.get('Location').startswith('magnet:'):
                return req.headers.get('Location')

    return req.content


def read_from_file(filepath: str) -> bytes:
    """Binary content from torrent file

    Args:
        filepath (str): path of torrent file

    Returns:
        bytes: binary content
    """
    with open(filepath, 'rb') as f:
        content = f.read()
    return content


def extract_tracker_url_from_announce(announce_url) -> urllib.parse.SplitResult:
    """Extract tracker url (http or udp) from annouce url

    Args:
        announce_url (str): url of tracker announce

    Returns:
        urlib.parse.SplitResult: url split
    """
    split_url = urllib.parse.urlsplit(announce_url)
    tracker_url = urllib.parse.SplitResult(
        split_url.scheme, split_url.netloc, None, None, None
    )
    return tracker_url


def read_resource(resource, headers: dict = {}) -> bytes:
    """Read torrent file resource (bytes, file, url)

    inspired by _open_resource: https://github.com/kurtmckee/feedparser/blob/develop/feedparser/api.py

    Args:
        resource ([bytes, filepath, url]): torrent file resource
        headers (dict): header argument to requests

    Returns:
        bytes: binary content
    """
    if isinstance(resource, str):
        if resource.split(':')[0] == 'magnet':
            raise NotImplementedError("Magnet link are not supported")
        if urllib.parse.urlsplit(resource)[0] in ['http', 'https', 'file', 'ftp']:
            return read_from_url(resource, headers=headers)

    try:
        return read_from_file(resource)
    except (IOError, UnicodeEncodeError, TypeError, ValueError):
        pass

    if not isinstance(resource, bytes):
        return resource.encode('utf-8')

    return resource
