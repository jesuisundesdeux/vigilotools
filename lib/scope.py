#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re

import pandas as pd

import lib.net as net

CITYLIST = "https://vigilo-bf7f2.firebaseio.com/citylist.json"


def get_scope_list(no_cache=False,beta=False):
    """Get scope list"""
    cachefile = '/tmp/scopes_list.csv'
    df = None
    if no_cache or not os.path.exists(cachefile):
        data = net.get_url_content(CITYLIST)
        loadedscopes = json.loads(data)
        scopes = {}
        ignoredkey = []
        for key in loadedscopes.keys():
            try:
                scopeid = loadedscopes[key]['scope']
                del loadedscopes[key]['scope']

                # Ignore #montpellier beta instance (duplicated contents with 34_montpellier scope)
                if scopeid == '00_test':
                    ignoredkey.append(key)
                    continue

                scopes[scopeid] = loadedscopes[key]
                scopes[scopeid]['name'] = key
                scopes[scopeid]['api_path'] = scopes[scopeid]['api_path'].replace(
                    '%3A%2F%2F', '://')
                scopes[scopeid]['api_path'] = re.sub(
                    r"/$", "", scopes[scopeid]['api_path'])

                # Populate more scope informations
                scopeurl = f"{scopes[scopeid]['api_path']}/get_scope.php?scope={scopeid}"
                data = net.get_url_content(scopeurl)
                scope_more_info = json.loads(data)

                # Contact
                scopes[scopeid]['contact'] = scope_more_info['contact_email']
                scopes[scopeid]['contact'] = "xxxx" + re.sub(
                    r'.*@', '@', scopes[scopeid]['contact'])

                scopes[scopeid]['department'] = scope_more_info['department']
                scopes[scopeid]['version'] = scope_more_info['backend_version'] if loadedscopes[key]['prod'] else 'Beta'
            except:
                print(f"!!! Scope {key} ignored !!!")
                ignoredkey.append(key)

        for key in ignoredkey:
            del loadedscopes[key]

        # Convert to pandas dataframe
        df = pd.DataFrame.from_dict(scopes, orient='index')
        df.index.names = ['scopeid']

        df.to_csv(cachefile)
    else:
        df = pd.read_csv(filepath_or_buffer=cachefile, index_col="scopeid")

    # If not Beta, only select prod scope version
    if not beta:
        mask = ~df.version.str.contains(pat="Beta", case=False)
        df = df[mask]

    df = df.reindex(sorted(df.columns), axis=1)
    return df
