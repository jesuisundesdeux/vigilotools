#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import click
import importlib
from core.cmd import pass_context


CONTEXT_SETTINGS = dict(auto_envvar_prefix='VGTOOL')


# class Context(object):
#     pass


# pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__)))


class MyCMD(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for cmdname in os.listdir(cmd_folder):
            dirname = os.path.join(cmd_folder, cmdname)
            if not cmdname.startswith('__') and os.path.isdir(dirname):
                fullpath = os.path.join(dirname, '__init__.py')
                print(fullpath)
                if os.path.exists(fullpath):
                    rv.append(cmdname)

        rv.sort()
        return rv

    def get_command(self, ctx, name):
        mod = importlib.import_module(f'core.poster.{name}')
        try:
            mod = importlib.import_module(f'core.poster.{name}')
        except ImportError:
            return
        return mod.cli


@click.command(cls=MyCMD, context_settings=CONTEXT_SETTINGS)
@pass_context
def cli(ctx):
    """Poster generation"""
    pass
