#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import json
import click
import importlib
import urllib.request
from tabulate import tabulate

from PIL import Image, ImageDraw, ImageFont


DIST = 500

VERSION = "0.0.1"

TEMPLATE = "parodie_stop_incivilite_montpellier"
TEMPLATEDIR = f"templates"
TEMPLATEFULLDIR = f"templates/{TEMPLATE}"


ISSUE_PICTURE = "lodeve.png"
COLUMN_WIDTH = 50

API = "https://api-vigilo.jesuisundesdeux.org"


def loadTemplate(templatename):
    module = importlib.import_module(f'templates.{templatename}')
    moduleClass = getattr(module, f"TPL{templatename}")
    return moduleClass()


# test = loadTemplate(TEMPLATE)
# test.generate(API, ISSUE_PICTURE)


@click.group()
def cli():
    pass


@cli.group('list')
def list():
    """List a type object"""


@cli.command()
@click.option('--scope', '-s', default="34_montpellier", help='Select city scope name')
@click.option('--template', '-t', default="parodie_stop_incivilite_montpellier", help='Select template')
@click.argument('token', type=str)
def generate(scope, template, token):
    """Generate a poster"""

    test = loadTemplate(template)
    test.set_scope(scope)
    test.generate(token)
    sys.exit()

    api_path = get_scope_information(scope)['api_path']

    # Get issue information
    issue_url = f'{api_path}/get_issues.php?token={token}'
    data = download_url(issue_url)
    issue = json.loads(data)
    if len(issue) > 1:
        raise Exception("More issues")

    issue = issue[0]
    category = int(issue['categorie'])
    lat = float(issue['coordinates_lat'])
    lon = float(issue['coordinates_lon'])
    geopoint_issue = geopy.Point(lat, lon)

    if category != CATEGORY:
        raise Exception(
            f"Category no coresponding with incivility theme")

    # Select issues
    list_issue = {'total': {}}
    issues_url = f'{api_path}/get_issues.php?c={category}'
    data = download_url(issues_url)
    issues = json.loads(data)
    for i in issues:
        geopoint_search = geopy.Point(
            float(i['coordinates_lat']), float(i['coordinates_lon']))
        dist = geopy.distance.distance(geopoint_issue, geopoint_search).m
        if dist <= 500:
            # print(i['token'])
            img_filename = f"/tmp/{i['token']}.png"
            if not os.path.exists(img_filename):
                photo_url = f"{api_path}/get_photo.php?token={i['token']}"

                print(f"Download {img_filename}")
                download_url_to_file(photo_url, img_filename)
            img = Image.open(img_filename)

            cropped = img.crop_to_aspect(480, 480)
            cropped.thumbnail((480, 480), Image.ANTIALIAS)
            cropped.save(f"/tmp/thumb_{i['token']}.png")
            # list_issue.append(i)
            ratio = img.size[0] / img.size[1]
            if ratio not in list_issue['total']:
                list_issue['total'][ratio] = 0

            list_issue['total'][ratio] += 1

            if ratio not in list_issue:
                list_issue[ratio] = []

            list_issue[ratio].append(i)

    s = [(k, list_issue['total'][k])
         for k in sorted(list_issue['total'], key=list_issue['total'].get, reverse=True)]

    topkey = s[0][0]
    for i in list_issue[topkey]:
        img_filename = f"/tmp/{i['token']}.png"
        img = Image.open(img_filename)
        print(img.size)

# test = loadTemplate(templatename)
# test.info()
# list_templates.append([templatename, test.info()])

# print(get_scope_information(scope))
# click.echo(template)
# click.echo(token)


# @cli.command()
# @click.option('--name', default="toto", help='Number of greetings.')
# def generate_poster(name="toto"):
#     click.echo(name)


@list.command('scope')
def list_scope():
    """Liste les scopes disponible"""
    data = download_url(CITYLIST)
    scopes = json.loads(data)

    list_scopes = []
    for key in scopes.keys():
        list_scopes.append([scopes[key]['scope'], key])

    header = ['Scope Id', 'Scope name']
    print(tabulate(list_scopes, headers=header, tablefmt="orgtbl"))


@list.command('template')
def list_template():
    """Liste les templates"""

    list_templates = []
    for templatename in os.listdir(TEMPLATEDIR):
        test = loadTemplate(templatename)
        test.info()
        list_templates.append([templatename, test.info()])

    header = ['Template', 'Description']
    print(tabulate(list_templates, headers=header, tablefmt="orgtbl"))

    # data = download_url("%s/get_scope.php?scope=%s" %
    #                     (scope_info['api_path'], scope_info['scope']))
    # scope_info = json.loads(data)

    # click.echo(scope)


if __name__ == '__main__':
    cli()
