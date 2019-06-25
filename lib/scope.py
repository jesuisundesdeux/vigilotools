#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import lib.net as net
CITYLIST = "https://vigilo-bf7f2.firebaseio.com/citylist.json"


def get_scope_list(no_cache=False):
    cachefile = '/tmp/collage_scope.json'
    if no_cache or not os.path.exists(cachefile):
        data = net.get_url_content(CITYLIST)
        scopes = json.loads(data)

        for key in scopes.keys():
            scopes[key]['api_path'] = scopes[key]['api_path'].replace(
                '%3A%2F%2F', '://')
    else:
        with open(cachefile) as jsonfile:
            scopes = json.load(jsonfile)

    return scopes


def get_scope_information(scopeid, no_cache=False):
    """Get scope information with cache support"""
    scopes = get_scope_list(no_cache)
    scope = None
    for key in scopes.keys():
        if scopeid in scopes[key]['scope']:
            scopes[key]['api_path'] = scopes[key]['api_path'].replace(
                '%3A%2F%2F', '://')

            scope = scopes[key]
            break

    return scope
