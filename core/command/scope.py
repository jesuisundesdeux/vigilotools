#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import click
import urllib.request
from tabulate import tabulate
from core.cmd import pass_context

CITYLIST = "https://vigilo-bf7f2.firebaseio.com/citylist.json"


def download_url(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    return text


@click.group()
@pass_context
def cli(ctx):
    """Information des scopes"""
    pass


@cli.command("list")
def list_cmd():
    """Liste les scopes"""
    data = download_url(CITYLIST)
    scopes = json.loads(data)

    list_scopes = []
    for key in scopes.keys():
        list_scopes.append([scopes[key]['scope'], key])

    header = ['Scope Id', 'Scope name']
    print(tabulate(list_scopes, headers=header, tablefmt="orgtbl"))
