#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib.request

import click
from tabulate import tabulate

from core.cmd import pass_context
import lib.scope


@click.group()
@pass_context
def cli(ctx):
    """Scopes informations"""
    pass


@cli.command("list")
def list_cmd():
    """Scopes list"""
    scopes = lib.scope.get_scope_list()

    list_scopes = []
    for key in scopes.keys():
        list_scopes.append([scopes[key]['scope'], key])

    header = ['Scope ID', 'Scope name']
    print(tabulate(list_scopes, headers=header, tablefmt="orgtbl"))


@click.option('-s', '--scope', required=True)
@cli.command()
def show(scope):
    """Show scope informations"""
    scopes = lib.scope.get_scope_list()

    show_scope = None
    for key in scopes.keys():
        current_scope = scopes[key]['scope']
        if scope == current_scope:
            show_scope = [[
                scopes[key]['scope'],
                key,
                scopes[key]['country'],
                'X' if scopes[key]['prod'] else '',
                scopes[key]['api_path'].replace('%3A%2F%2F', '://')
            ]]
        # list_scopes.append([scopes[key]['scope'], key])

    header = ['Scope ID', 'Scope name', 'Country', 'In prod', 'API']
    print(tabulate(show_scope, headers=header, tablefmt="fancy_grid"))
