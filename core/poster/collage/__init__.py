#!/usr/bin/env python
# -*- coding: utf-8 -*-import os

"""
A collage poster generator
"""
import collections
import datetime
import inspect
import json
import math
import os
import random
import sys
import time
import urllib.request

import click
import geopy
import geopy.distance
from PIL import Image, ImageColor, ImageDraw, ImageFont

import lib.image
import lib.issue
import lib.scope
from core.cmd import pass_context

CATEGORY = 2
DISTANCE = 100000

MAXPICTURES = 1000
MAX_SEARCH_ITERATION_RATIO = 10


class Collage():
    """
    Collage class
    """

    def __init__(self):
        self.dir = os.path.dirname(__file__)
        self.debug = False
        self.img_text_options = {
            'background': "#000000",
            'color': "#FFFFFF",
            'size': 16,
            'text': ""
        }
        self.title_text_options = {
            'background': "#000000",
            'color': "#FFFFFF",
            'size': 36,
            'text': ""
        }
        self.scope = None
        self.issues = []
        self.api_path = None
        self.loaded_issues = None
        self.filtered_issues = None
        self.no_cache = False

    def set_debug(self, debug):
        """Set debug proprety"""
        self.debug = debug

    def set_issues(self, issues):
        """Set issues proprety"""
        self.issues = issues

    def set_nocache(self, no_cache):
        """Define nocache property"""
        self.no_cache = no_cache

    def set_img_text_options(self, background, color, margin, size, text):
        """Define img_text options property"""
        self.img_text_options = {
            'background': background,
            'color': color,
            'margin': margin,
            'size': size,
            'text': text
        }

    def set_title_text_options(self, background, color, margin, size, text):
        """Define title_text options property"""
        self.title_text_options = {
            'background': background,
            'color': color,
            'margin': margin,
            'size': size,
            'text': text
        }

    def set_scope(self, scope):
        """Define scope property"""
        self.scope = scope
        self.api_path = lib.scope.get_scope_information(scope, self.no_cache)[
            'api_path']

    def download_image(self, token):
        """Download image"""
        img_filename = f"/tmp/{token}.png"

        if not os.path.exists(img_filename):
            print(f"Download image {token}")
            photo_url = f"{self.api_path}/get_photo.php?token={token}"
            print(photo_url)
            download_url_to_file(photo_url, img_filename)

    def generate(self, width, outputname):
        """Generate collage poster"""

        if not self.issues:
            return

        # Download images
        issues = []
        for issue in self.issues:
            filename = f"/tmp/{issue['token']}.png"
            try:
                self.download_image(issue['token'])

                # Verify is image not corupted
                img = Image.open(filename)
                img.crop((1, 1, 2, 2))

                issues.append(issue)
            except urllib.error.HTTPError:
                print(f"### ERROR DOWNLOAD {filename}")
            except OSError:
                print(f"### IMAGE ERROR {filename}")

        nb_images = len(issues)

        (max_images, nb_cols, _) = search_best_grid_dimension(
            nb_images, MAX_SEARCH_ITERATION_RATIO)

        selected_issues = issues[:max_images]

        # Generate collage
        selected_issues.reverse()
        initial_height = int(width/nb_cols)
        collage_image = lib.image.make_collage(
            selected_issues,  self.img_text_options, width, initial_height)

        if self.title_text_options['text'] == "":
            collage_image.save(outputname)
            return

        # Title box
        font = ImageFont.truetype(
            f'Cantarell-ExtraBold.otf', self.title_text_options['size'])
        dt = ImageDraw.Draw(collage_image)
        twidth, theight = dt.textsize(
            self.title_text_options['text'], font=font)
        boxheight = theight+(2*self.img_text_options['margin'])

        color = ImageColor.getrgb(self.title_text_options['background'])
        newimage = Image.new(
            'RGB', (collage_image.size[0], collage_image.size[1]+boxheight), color)

        newimage.paste(collage_image, (0, 0))
        color = ImageColor.getrgb(self.title_text_options['color'])
        d = ImageDraw.Draw(newimage)
        d.text(((newimage.size[0]-twidth)/2, collage_image.size[1]+self.img_text_options['margin']), self.title_text_options['text'],
               font=font, fill=color)

        newimage.save(outputname)


def proper_divs2(number):
    """Search divisors"""
    return [x for x in range(1, (number + 1) // 2 + 1) if number % x == 0 and number != x]


def search_best_grid_dimension(nb_images, max_ratio):
    """Search best grid collage dimension"""
    best_number = nb_images
    best_grid = get_grid_dimenssion(nb_images)

    for i in range(0, MAX_SEARCH_ITERATION_RATIO):
        current_number = nb_images - i
        grid = get_grid_dimenssion(current_number)
        ratio = grid[0] / float(grid[1])
        if ratio < max_ratio:
            best_number = current_number
            best_grid = grid
            break

    return (best_number, best_grid[0], best_grid[1])


def get_grid_dimenssion(nb_images):
    """Get collage picture grid dimension"""
    square = math.sqrt(nb_images)
    intsquare = int(square)
    issquare = square == intsquare
    if issquare:
        return(intsquare, intsquare)

    divisors = proper_divs2(nb_images)
    if len(divisors) == 1:
        return (int(square), int(square))

    idx = 0
    idx_divisor = -1
    for divisor in divisors:
        if divisor > square:
            idx_divisor = idx
            break
        idx += 1

    if idx_divisor > 0:
        return (divisors[idx_divisor], divisors[idx_divisor-1])

    return (-1, -1)


def download_url_to_file(url, filename):
    """Download url to file"""
    urllib.request.urlretrieve(url, filename)


@click.group()
def cli():
    """Multiples photos collage"""


@click.option('-s', '--scope', required=True, help='Scope ID')
@click.option('-l', '--limit', default=100, help='Limit issues', show_default=True)
@click.option('-o', '--output', default='/tmp/collage.jpg', help='Output filename',
              show_default=True)
# Image options
@click.option('--width', '--iw', default=2048, help='Width output image',
              show_default=True)
@click.option('--img-background', '--ib', default="", help='Background color image ex: #000000',
              show_default=True)
@click.option('--img-color', '--ic', default="#FFFFFF", help='Text color image. ex: #FFFFFF',
              show_default=True)
@click.option('--img-text', '--it', default="", help='Text for all images: Ex: "date: {datetime}"',
              show_default=True)
@click.option('--img-textmargin', '--im', default=3, help='Img text margin',
              show_default=True)
@click.option('--img-textsize', '--is', default=16, help='Img text size',
              show_default=True)
# Title options
@click.option('--title-text', '--tt', default="", help='Title text',
              show_default=True)
@click.option('--title-textmargin', '--tm', default=3, help='Title text margin',
              show_default=True)
@click.option('--title-background', '--tb', default="#000000", help='Background title color. ex: #000000',
              show_default=True)
@click.option('--title-color', '--tc', default="#FFFFFF", help='Title text color. ex: #FFFFFF',
              show_default=True)
@click.option('--title-textsize', '--ts', default=36, help='Title text size',
              show_default=True)
@click.option('-n', '--no-cache', is_flag=True, help='No cache remote issues file')
@click.option('-a', '--filter-address', multiple=True, help='Add address filter')
@click.option('-c', '--filter-category',  multiple=True, help='Add category filter')
@click.option('-t', '--filter-token', multiple=True, help='Add token filter')
@click.option('-d', '--filter-date', nargs=2, multiple=True, help='Add timestamp filter. Ex: 2019-01-07 2019-01-14', metavar='[START END]')
@click.option('-n', '--filter-near', multiple=True, metavar='[TOKEN]', help='Add token for searching near observations')
@click.option('-m', '--max-distance', default=50,  help='max near distance')
@cli.command("filter")
@pass_context
def generate_filter(ctx,
                    scope,
                    output,
                    img_background,
                    img_color,
                    img_textmargin,
                    img_textsize,
                    img_text,
                    title_background,
                    title_color,
                    title_textmargin,
                    title_textsize,
                    title_text,
                    filter_address,
                    filter_category,
                    filter_token,
                    filter_date,
                    filter_near,
                    max_distance,
                    width,
                    no_cache,
                    limit
                    ):
    "Generate from all issues"

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
    cissues.add_filter('date', filter_date)
    cissues.add_filter('token', filter_token)
    cissues.add_filter('near', filter_near)
    cissues.add_filter('category', filter_category)
    cissues.do_filters()

    issues = cissues.get_filtered_issues()

    ########

    # Collage configuration
    collage = Collage()
    collage.set_debug(ctx.debug)
    collage.set_issues(issues)
    collage.set_scope(scope)
    collage.set_nocache(no_cache)
    collage.set_img_text_options(
        background=img_background,
        color=img_color,
        margin=img_textmargin,
        size=img_textsize,
        text=img_text
    )
    collage.set_title_text_options(
        background=title_background,
        color=title_color,
        margin=title_textmargin,
        size=title_textsize,
        text=title_text
    )

    collage.generate(width, output)
