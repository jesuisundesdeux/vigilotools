#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request


def get_url_content(url):
    """Get url content"""
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode('utf-8')

    except urllib.error.HTTPError:
        print(f"Error for downloading Url: {url}")
        raise

    return text
