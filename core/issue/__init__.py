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


@click.option('-s', '--scope', required=True, help='Scope ID')
@click.option('-l', '--limit', default=-1, help='Limit issues', show_default=True)
@click.option('-f', '--field', default=['token', 'date', 'address', 'categorie'], multiple=True, help="Show fields")
@click.option('--no-cache', is_flag=True, help='No cache remote issues file')
@click.option('--filter-address', '--fa', multiple=True, help='Add address filter')
@click.option('--filter-category', '--fc',  multiple=True, help='Add category filter')
@click.option('--filter-token', '--ft', multiple=True, help='Add token filter')
@click.option('--filter-date', '--fd', nargs=2, multiple=True, metavar='[START END]', help='Add timestamp filter. Ex: 2019-01-07 2019-01-14')
@click.option('--filter-near', '--fn', multiple=True, metavar='[TOKEN]', help='Add token for searching near observations')
@click.option('--filter-string', '--fs', multiple=True, help='Add string for searching near observations')
@click.option('--max-distance', default=50, help='max near distance')
@cli.command("list")
@pass_context
def list_cmd(ctx, scope, limit, field, no_cache, filter_address,
             filter_category, filter_token, filter_near, filter_string,
             max_distance, filter_date):
    """Issues list"""

    # Set issues property
    cissues = lib.issue.Issues()
    cissues.set_debug(ctx.debug)
    cissues.set_scope(scope)
    cissues.set_nocache(no_cache)
    cissues.set_limit(limit)
    cissues.set_maxdistance(max_distance)

    # Do filter
    cissues.load_all_issues()
    cissues.add_filter('address', filter_address)
    cissues.add_filter('category', filter_category)
    cissues.add_filter('token', filter_token)
    cissues.add_filter('date', filter_date)
    cissues.add_filter('near', filter_near)
    cissues.add_filter('string', filter_string)
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
    cissues.load_all_issues()
    issues = cissues.get_field_names()

    for field in issues:
        print(field)
