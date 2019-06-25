#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request


def get_url_content(url):
    """Get url content"""
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    return text
