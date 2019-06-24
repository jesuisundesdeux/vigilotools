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
from PIL import Image, ImageDraw, ImageFont, ImageColor

from core.cmd import pass_context

CATEGORY = 2
DISTANCE = 100000

MAXPICTURES = 1000
MAX_SEARCH_ITERATION_RATIO = 10

CITYLIST = "https://vigilo-bf7f2.firebaseio.com/citylist.json"


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
        self.limit = None
        self.api_path = None
        self.loaded_issues = None
        self.filtered_issues = None
        self.no_cache = False
        self.filters = {}

    def set_debug(self, debug):
        """Set debug proprety"""
        self.debug = debug

    def set_nocache(self, no_cache):
        """Define nocache property"""
        self.no_cache = no_cache

    def set_img_text_options(self, background, color, size, text):
        """Define img_text options property"""
        self.img_text_options = {
            'background': background,
            'color': color,
            'size': size,
            'text': text
        }

    def set_title_text_options(self, background, color, size, text):
        """Define title_text options property"""
        self.title_text_options = {
            'background': background,
            'color': color,
            'size': size,
            'text': text
        }

    def set_scope(self, scope):
        """Define scope property"""
        self.scope = scope
        self.api_path = get_scope_information(scope, self.no_cache)['api_path']

    def set_limit(self, limit):
        """Define limit property"""
        self.limit = limit

    def get_all_issues(self):
        """Get all issues from scope"""

        if self.api_path is None:
            raise Exception("Please define scope")

        cachefile = '/tmp/collage_issues.json'
        if self.no_cache or not os.path.exists(cachefile):
            issue_url = f'{self.api_path}/get_issues.php'
            data = get_url_content(issue_url)
            self.loaded_issues = json.loads(data)

            for issue in self.loaded_issues:
                # Add date field
                issue['timestamp'] = issue['time']
                dtime = datetime.datetime.fromtimestamp(
                    int(issue['timestamp']))
                issue['date'] = dtime.strftime('%Y-%m-%d')
                issue['time'] = str(dtime.time)

            with open(cachefile, 'w') as jsonfile:
                json.dump(self.loaded_issues, jsonfile)
        else:
            with open(cachefile) as jsonfile:
                self.loaded_issues = json.load(jsonfile)

        self.filtered_issues = self.loaded_issues[:]

    def get_filtered_issues(self):
        """Get filter issues(add_by)"""
        if not self.limit:
            return self.filtered_issues

        return self.filtered_issues[:self.limit]

    def add_by(self, ftype, values):
        """ Set add_by property"""
        self.filters[ftype] = values

    def filter_all(self):
        """Filters issues with some filters"""
        self.filtered_issues = []
        if not self.filters:
            return

        self.filtered_issues = []
        for item in self.loaded_issues:
            count = 0
            for ftype in self.filters:
                if getattr(self, f"filter_by_{ftype}")(item):
                    count += 1

            if count == len(self.filters):
                self.filtered_issues.append(item)

    def filter_by_address(self, item):
        """Add by address filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')
        if not self.filters[ftype]:
            return True

        for search in self.filters[ftype]:
            if search.lower() in item['address'].lower() and item not in self.filtered_issues:
                return True

        return False

    def filter_by_category(self, item):
        """Add by category filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')
        if not self.filters[ftype]:
            return True

        for search in self.filters[ftype]:
            if search == item['categorie'] and item not in self.filtered_issues:
                return True

        return False

    def filter_by_date(self, item):
        """Add by date filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')
        if not self.filters[ftype]:
            return True

        for dates in self.filters[ftype]:
            start, end = dates

            tstart = time.mktime(datetime.datetime.strptime(
                start, "%Y-%m-%d").timetuple())
            tend = time.mktime(datetime.datetime.strptime(
                end, "%Y-%m-%d").timetuple())

            if int(item['timestamp']) >= tstart and int(item['timestamp']) <= tend and item not in self.filtered_issues:
                return True
                break

        return False

    def filter_by_token(self, item):
        """Add by token filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')
        if not self.filters[ftype]:
            return True

        for search in self.filters[ftype]:
            if search == item['token'] and item not in self.filtered_issues:
                return True

        return False

    def download_image(self, token):
        """Download image"""
        img_filename = f"/tmp/{token}.png"

        if not os.path.exists(img_filename):
            print(f"Download image {token}")
            photo_url = f"{self.api_path}/get_photo.php?token={token}"
            print(photo_url)
            download_url_to_file(photo_url, img_filename)

    def export(self):
        if not self.get_filtered_issues():
            return

        print(self.get_filtered_issues())

    def generate(self, width, outputname):
        """Generate collage poster"""

        if not self.get_filtered_issues():
            return

        # Download images
        issues = []
        for issue in self.get_filtered_issues():
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
        collage_image = self.make_collage(
            selected_issues, outputname, width, initial_height)

        if self.title_text_options['text'] == "":
            collage_image.save(outputname)
            return

        boxheight = 60
        color = ImageColor.getrgb(self.title_text_options['background'])
        newimage = Image.new(
            'RGB', (collage_image.size[0], collage_image.size[1]+boxheight), color)

        newimage.paste(collage_image, (0, 0))
        d = ImageDraw.Draw(newimage)
        font = ImageFont.truetype(
            f'Cantarell-ExtraBold.otf', self.title_text_options['size'])
        twidth, _ = d.textsize(self.title_text_options['text'])
        color = ImageColor.getrgb(self.title_text_options['color'])
        d.text(((newimage.size[0]-twidth)/2, newimage.size[1]-boxheight+7), self.title_text_options['text'],
               font=font, fill=color)

        newimage.save(outputname)

    def make_collage(self, issues, filename, width, init_height):
        # Source: https://github.com/delimitry/collage_maker
        """
        Make a collage image with a width equal to `width` from `images` and save to `filename`.
        """
        if not issues:
            print('No images for collage found!')
            return False

        margin_size = 2
        # run until a suitable arrangement of images is found
        while True:
            # copy images to images_list
            issues_list = issues[:]
            coefs_lines = []
            images_line = []
            x_pos = 0
            while issues_list:
                # get first image and resize to `init_height`
                issue = issues_list.pop(0)
                img_path = f"/tmp/{issue['token']}.png"
                img = Image.open(img_path)
                img.thumbnail((width, init_height))

                # when `x` will go beyond the `width`, start the next line
                if x_pos > width:
                    coefs_lines.append((float(x_pos) / width, images_line))
                    images_line = []
                    x_pos = 0
                x_pos += img.size[0] + margin_size
                images_line.append(issue)

            # finally add the last line with images
            coefs_lines.append((float(x_pos) / width, images_line))

            # compact the lines, by reducing the `init_height`, if any with one or less images
            if len(coefs_lines) <= 1:
                break
            if any(map(lambda c: len(c[1]) <= 1, coefs_lines)):
                # reduce `init_height`
                init_height -= 10
            else:
                break

        # get output height
        out_height = 0
        for coef, imgs_line in coefs_lines:
            if imgs_line:
                out_height += int(init_height / coef) + margin_size
        if not out_height:
            print('Height of collage could not be 0!')
            return False

        collage_image = Image.new(
            'RGB', (width, int(out_height)), (35, 35, 35))
        # put images to the collage
        y_pos = 0
        for coef, imgs_line in coefs_lines:
            if imgs_line:
                x_pos = 0
                for issue in imgs_line:
                    img_path = f"/tmp/{issue['token']}.png"
                    img = Image.open(img_path)
                    # if need to enlarge an image - use `resize`, otherwise use `thumbnail`, it's faster
                    k = (init_height / coef) / img.size[1]
                    if k > 1:
                        img = img.resize(
                            (int(img.size[0] * k), int(img.size[1] * k)), Image.ANTIALIAS)
                    else:
                        img.thumbnail(
                            (int(width / coef), int(init_height / coef)), Image.ANTIALIAS)

                    d = ImageDraw.Draw(img)
                    font = ImageFont.truetype(
                        f'Cantarell-Regular.otf', self.img_text_options['size'])
                    imgtextheight = 26

                    if self.img_text_options['background'] != "":
                        color = ImageColor.getrgb(
                            self.img_text_options['background'])
                        d.rectangle(
                            ((0, img.size[1]-imgtextheight), (img.size[0], img.size[1])), fill=color, outline=color, width=8)

                    twidth, theight = d.textsize(
                        self.img_text_options['text'].format(**issue))
                    if twidth < img.size[0]:
                        color = ImageColor.getrgb(
                            self.img_text_options['color'])
                        d.text(((img.size[0]-twidth)/2, img.size[1]-imgtextheight+int((imgtextheight-theight)/2)), self.img_text_options['text'].format(**issue),
                               font=font, fill=color)

                    if collage_image:
                        collage_image.paste(img, (int(x_pos), int(y_pos)))
                    x_pos += img.size[0] + margin_size
                y_pos += int(init_height / coef) + margin_size
        # collage_image.save(filename)
        return collage_image


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


def get_url_content(url):
    """Get url content"""
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    return text


def download_url_to_file(url, filename):
    """Download url to file"""
    urllib.request.urlretrieve(url, filename)


def get_scope_information(scopeid, no_cache):
    """Get scope information with cache support"""
    cachefile = '/tmp/collage_scope.json'
    if no_cache or not os.path.exists(cachefile):
        data = get_url_content(CITYLIST)
        jcities = json.loads(data)

        jscope = None
        for key in jcities.keys():
            if scopeid in jcities[key]['scope']:
                jcities[key]['api_path'] = jcities[key]['api_path'].replace(
                    '%3A%2F%2F', '://')

                jscope = jcities[key]
                break

        with open(cachefile, 'w') as jsonfile:
            json.dump(jscope, jsonfile)
    else:
        with open(cachefile) as jsonfile:
            jscope = json.load(jsonfile)

    return jscope


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
@click.option('--img-text', '--it', default="", help='Text for all images: Ex: "date: {datetime}"',
              show_default=True)
@click.option('--img-background', '--ib', default="", help='Background color image ex: #000000',
              show_default=True)
@click.option('--img-color', '--ic', default="#FFFFFF", help='Text color image. ex: #FFFFFF',
              show_default=True)
@click.option('--img-textsize', '--is', default=16, help='Img text size',
              show_default=True)
# Title options
@click.option('--title-text', '--tt', default="", help='Title text',
              show_default=True)
@click.option('--title-background', '--tb', default="#000000", help='Background title color. ex: #000000',
              show_default=True)
@click.option('--title-color', '--tc', default="#FFFFFF", help='Title text color. ex: #FFFFFF',
              show_default=True)
@click.option('--title-textsize', '--ts', default=36, help='Title text size',
              show_default=True)
@click.option('-n', '--no-cache', is_flag=True, help='No cache remote issues file')
@click.option('-a', '--add-address', multiple=True, help='Add address filter')
@click.option('-c', '--add-category',  multiple=True, help='Add category filter')
@click.option('-t', '--add-token', multiple=True, help='Add token filter')
@click.option('-d', '--add-date', nargs=2, multiple=True, help='Add timestamp filter. Ex: 2019-01-07 2019-01-14', metavar='[START END]')
@cli.command("all")
@pass_context
def generate_all(ctx,
                 scope,
                 output,
                 img_background,
                 img_color,
                 img_textsize,
                 img_text,
                 title_background,
                 title_color,
                 title_textsize,
                 title_text,
                 add_address,
                 add_category,
                 add_token,
                 add_date,
                 width,
                 no_cache,
                 limit
                 ):
    "Generate from all issues"

    # Collage configuration
    collage = Collage()
    collage.set_debug(ctx.debug)
    collage.set_scope(scope)
    collage.set_nocache(no_cache)
    collage.set_limit(limit)
    collage.set_img_text_options(
        background=img_background,
        color=img_color,
        size=img_textsize,
        text=img_text
    )
    collage.set_title_text_options(
        background=title_background,
        color=title_color,
        size=title_textsize,
        text=title_text
    )

    # Generate collage
    collage.get_all_issues()
    collage.add_by('address', add_address)
    collage.add_by('category', add_category)
    collage.add_by('date', add_date)
    collage.add_by('token', add_token)
    collage.add_by('category', add_category)
    collage.filter_all()
    collage.generate(width, output)
    # collage.export()
