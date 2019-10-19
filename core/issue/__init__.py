#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import locale
import os

import click
import cv2 as cv
import imutils
import numpy as np
from tabulate import tabulate

import lib.file
import lib.issue
from core.cmd import pass_context

from wand.image import Image


# # https: // gist.github.com/jacobtolar/fb80d5552a9a9dfc32b12a829fa21c0c
# class MutuallyExclusiveOption(click.Option):
#     def __init__(self, *args, **kwargs):
#         self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
#         help = kwargs.get('help', '')
#         if self.mutually_exclusive:
#             ex_str = ', '.join(self.mutually_exclusive)
#             kwargs['help'] = help + (
#                 ' NOTE: This argument is mutually exclusive with '
#                 ' arguments: [' + ex_str + '].'
#             )
#         super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

#     def handle_parse_result(self, ctx, opts, args):
#         if self.mutually_exclusive.intersection(opts) and self.name in opts:
#             raise click.UsageError(
#                 "Illegal usage: `{}` is mutually exclusive with "
#                 "arguments `{}`.".format(
#                     self.name,
#                     ', '.join(self.mutually_exclusive)
#                 )
#             )

#         return super(MutuallyExclusiveOption, self).handle_parse_result(
#             ctx,
#             opts,
#             args
#         )


@click.group()
@pass_context
def cli(ctx):
    """Issues informations"""


@click.option('-s', '--scope', multiple=True, help='[Scope ID ...], use [ALL] for use all scopes')
@click.option('-h', '--head', default=0, help='head', show_default=True)
@click.option('-t', '--tail', default=0, help='tail', show_default=True)
@click.option('-f', '--fields', default="ALL", help="Show fields. [ALL] or fieldsname. ex: token,date,time,address", show_default=True)
@click.option('-v', '--verbose', is_flag=True, help='Verbose mode')
@click.option('--imp', '--import', default="", help="Import CSV", show_default=False)
@click.option('--exp', '--export', default="", help="Export CSV", show_default=False)
@click.option('--no-cache', is_flag=True, help='No cache remote issues file')
@click.option('-i', '--ignore-token', '--it', multiple=True, help='Ignore token')
@click.option('--filter-address', '--fa', multiple=True, help='Add address filter')
@click.option('--filter-category', '--fc',  multiple=True, help='Add category filter')
@click.option('--filter-token', '--ft', multiple=True, help='Add token filter')
@click.option('--filter-date', '--fd', nargs=2, multiple=True, metavar='[START END]', help='Add timestamp filter. Ex: 2019-01-07 2019-01-14')
@click.option('--filter-near', '--fn', multiple=True, metavar='[TOKEN]', help='Add token for searching near observations')
@click.option('--filter-string', '--fs', multiple=True, help='Add string for searching near observations')
@click.option('--sort-by', '--sb', default="", help='sort by field')
@click.option('--group-by', '--gb', default="", help='group by')
# This argument is mutually exclusive with group-having', cls=MutuallyExclusiveOption, mutually_exclusive=["group_having"])
@click.option('--group-function', '--gf', default='',  help='group function columname:function[count,max,min,mean,%]')
# . This argument is mutually exclusive with group-function', cls=MutuallyExclusiveOption, mutually_exclusive=["group_function"])
@click.option('--having', '--gh', default='',  help='Select records by grouped records or counter records')
@click.option('--reverse', '--rs', is_flag=True, help='Reverse sorting')
@click.option('-p', '--populate', multiple=True, help='populate columen during loading data [image]')
@click.option('--max-distance', default=50, help='max near distance')
@cli.command("list")
@pass_context
def list_cmd(ctx, scope, fields, verbose, no_cache, ignore_token, filter_address,
             filter_category, filter_token, filter_near, filter_string,
             max_distance, filter_date, sort_by, group_by, group_function, having, reverse, head, tail, exp, imp, populate):
    """Issues list"""

    # Set french locale
    locale.setlocale(locale.LC_TIME, "fr_FR.utf8")

    # Set issues property
    cissues = lib.issue.Issues()
    cissues.set_debug(ctx.debug)
    cissues.set_scopes(scope)
    cissues.set_nocache(no_cache)
    cissues.set_maxdistance(max_distance)
    cissues.set_sortby(sort_by)
    cissues.set_groupby(group_by)
    cissues.set_groupfunction(group_function)
    cissues.set_having(having)
    cissues.set_reverse(reverse)
    cissues.set_head(head)
    cissues.set_tail(tail)
    cissues.set_fields(fields)
    cissues.set_populate(populate)
    cissues.set_verbose(verbose)

    # Load or import
    if imp:
        cissues.import_csv(imp)
    else:
        if not scope:
            raise Exception("Please define scope")

        cissues.load_all_issues()

    # Do filter
    cissues.add_filter('address', filter_address)
    cissues.add_filter('category', filter_category)
    cissues.add_filter('token', filter_token)
    cissues.add_filter('ignore', ignore_token)
    cissues.add_filter('date', filter_date)
    cissues.add_filter('near', filter_near)
    cissues.add_filter('string', filter_string)
    cissues.do_filters()

    # Get filtered issues
    cissues.output(exp)


@click.option('-s', '--scope', required=True, multiple=True, help='Scope ID')
@click.option('-f', '--field', default=[], multiple=True, help="Show fields")
@click.option('-n', '--no-cache', is_flag=True, help='No cache remote issues file')
@click.option('-t', '--token', multiple=True, help='Add token filter')
@click.option('-v', '--verbose', is_flag=True, help='Verbose mode')
@cli.command()
@pass_context
def show(ctx, scope, token, field, no_cache, verbose):
    """Show scope informations"""
    cissues = lib.issue.Issues()
    cissues.set_debug(ctx.debug)
    cissues.set_scopes(scope)
    cissues.set_nocache(no_cache)
    cissues.set_head(1)
    cissues.set_verbose(verbose)

    # Do filter
    cissues.load_all_issues()
    cissues.add_filter('token', token)
    cissues.do_filters()

    issues = cissues.get_filtered_issues()

    if len(issues) == 1:
        if field:
            showfields = field.split(',')
        else:
            showfields = list(issues.columns)

        for col in showfields:
            print(f'{col:>15} : {issues[col].values.item()}')
    else:
        raise Exception("More or not record")


@click.option('-s', '--scope', multiple=True, required=True, help='Scope ID')
@cli.command()
@pass_context
def fields(ctx, scope):
    """Show available issue fields"""
    cissues = lib.issue.Issues()
    cissues.set_debug(ctx.debug)
    cissues.set_scopes(scope)
    cissues.set_nocache(False)
    cissues.load_all_issues()
    fields = cissues.get_field_names()

    txtfields = ','.join(fields)
    size = len(txtfields)
    print("Available fields")
    print("-"*size)
    print(txtfields)
