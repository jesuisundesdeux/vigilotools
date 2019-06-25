#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib.request

import click
from tabulate import tabulate

import lib.issue
from core.cmd import pass_context


@click.group()
@pass_context
def cli(ctx):
    """Issues informations"""
    pass


@click.option('-s', '--scope', required=True, help='Scope ID')
@click.option('-l', '--limit', default=-1, help='Limit issues', show_default=True)
@click.option('-f', '--field', default=['token', 'date', 'address', 'categorie'], multiple=True, help="Show fields")
@click.option('-n', '--no-cache', is_flag=True, help='No cache remote issues file')
@click.option('-a', '--filter-address', multiple=True, help='Add address filter')
@click.option('-c', '--filter-category',  multiple=True, help='Add category filter')
@click.option('-t', '--filter-token', multiple=True, help='Add token filter')
@click.option('-d', '--filter-date', nargs=2, multiple=True, help='Add timestamp filter. Ex: 2019-01-07 2019-01-14', metavar='[START END]')
@cli.command("list")
@pass_context
def list_cmd(ctx, scope, limit, field, no_cache, filter_address, filter_category, filter_token, filter_date):
    """Issues list"""

    # Set issues property
    cissues = lib.issue.Issues()
    cissues.set_debug(ctx.debug)
    cissues.set_scope(scope)
    cissues.set_nocache(no_cache)
    cissues.set_limit(limit)

    # Do filter
    cissues.load_all_issues()
    cissues.add_filter('address', filter_address)
    cissues.add_filter('category', filter_category)
    cissues.add_filter('date', filter_date)
    cissues.add_filter('token', filter_token)
    cissues.add_filter('category', filter_category)
    cissues.do_filters()

    issues = cissues.get_filtered_issues()

    list_issues = []
    for issue in issues:
        linefields = []
        for col in field:
            linefields.append(issue[col])
        list_issues.append(linefields)

    list_issues.reverse()
    print(tabulate(list_issues, headers=field, tablefmt="orgtbl"))


@click.option('-s', '--scope', required=True, help='Scope ID')
@click.option('-f', '--field', default=[], multiple=True, help="Show fields")
@click.option('-n', '--no-cache', is_flag=True, help='No cache remote issues file')
@click.option('-t', '--token', multiple=True, help='Add token filter')
@cli.command()
@pass_context
def show(ctx, scope, token, field, no_cache):
    """Show scope informations"""
    cissues = lib.issue.Issues()
    cissues.set_debug(ctx.debug)
    cissues.set_scope(scope)
    cissues.set_nocache(no_cache)
    cissues.set_limit(1)

    # Do filter
    cissues.load_all_issues()
    cissues.add_filter('token', token)
    cissues.do_filters()

    issues = cissues.get_filtered_issues()

    if len(issues) == 1:
        if not field:
            field = issues[0].keys()

        for col in field:
            print(f'{col:>15} : {issues[0][col]}')


@click.option('-s', '--scope', required=True)
@cli.command()
@pass_context
def fields(ctx, scope):
    """Show available issue fields"""
    cissues = lib.issue.Issues()
    cissues.set_debug(ctx.debug)
    cissues.set_scope(scope)
    cissues.set_nocache(False)
    cissues.set_limit(1)

    # Do filter
    cissues.load_all_issues()
    issues = cissues.get_filtered_issues()

    if len(issues) > 0:
        for field in issues[0]:
            print(f'{field}')
