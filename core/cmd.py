#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import click
import importlib


CONTEXT_SETTINGS = dict(auto_envvar_prefix='VGTOOL')


class Context(object):

    def __init__(self):
        self.debug = False


pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__)))


class MyCMD(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for dirname in os.listdir(cmd_folder):
            fullpath = os.path.join(cmd_folder, dirname, '__init__.py')
            if os.path.exists(fullpath):
                rv.append(dirname)

        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = importlib.import_module(f'core.{name}')
        except ImportError:
            return
        return mod.cli


@click.command(cls=MyCMD, context_settings=CONTEXT_SETTINGS)
@click.option('-d', '--debug', is_flag=True,
              help='For debugging')
@pass_context
def cli(ctx, debug):
    """Vigilo command tools"""
    ctx.debug = debug
