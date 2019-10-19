#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import urllib.request


def download_url_to_file(url, filename):
    """Download url to file"""
    urllib.request.urlretrieve(url, filename)


def write_content_to_file(content, filename):
    with open(filename, 'w') as ofile:
        ofile.write(content)


def read_content_from_file(filename):
    data = ""
    with open(filename, 'r') as ifile:
        data = ifile.read().replace('\n', '')

    return data


def md5sum_file(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
