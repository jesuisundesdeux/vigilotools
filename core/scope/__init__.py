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
@click.option('-s', '--sortby', multiple=True, help="Sort result")
@click.option('-b', '--beta', is_flag=True, help='Select also Beta scope')
def list_cmd(sortby,beta):
    """Scopes list"""

    # If not defined sort parameter
    if not sortby:
        sortby = ['scopeid']

    # Sort by
    sortby = list(sortby)
    df_scopes = lib.scope.get_scope_list(beta=beta)

    df_scopes = df_scopes.sort_values(sortby)
    df_scopes = df_scopes[['name', 'version']]
    print(tabulate(df_scopes, headers='keys', tablefmt="orgtbl", showindex=True))


@click.option('-s', '--scope',  multiple=True, required=True)
@cli.command()
def show(scope):
    """Show scope informations"""
    scopes_list = lib.scope.get_scope_list(beta=True)
    scopeinfo = scopes_list.loc[list(scope)]
    print(tabulate(scopeinfo, headers='keys',
                   tablefmt="fancy_grid", showindex=True))
