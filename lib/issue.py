#!/usr/bin/env python
# -*- coding: utf-8 -*-import os

import datetime
import inspect
import json
import os
import time

import lib.net as net
import lib.scope


class Issues():
    """
    Issues class
    """

    def __init__(self):
        self.debug = False
        self.scope = None
        self.limit = -1
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

    def set_scope(self, scope):
        """Define scope property"""
        self.scope = scope
        self.api_path = lib.scope.get_scope_information(scope, self.no_cache)[
            'api_path']

    def set_limit(self, limit):
        """Define limit property"""
        self.limit = limit

    def get_filtered_issues(self):
        """Get filter issues(add_filter)"""
        if self.limit == -1:
            return self.filtered_issues

        return self.filtered_issues[:self.limit]

    def load_all_issues(self):
        """Get all issues from scope"""

        cachefile = f'/tmp/collage_issues_{self.scope}.json'
        if self.no_cache or not os.path.exists(cachefile):
            issue_url = f"{self.api_path}/get_issues.php"
            data = net.get_url_content(issue_url)
            self.loaded_issues = json.loads(data)

            for issue in self.loaded_issues:
                # Add date field
                issue['timestamp'] = issue['time']
                dtime = datetime.datetime.fromtimestamp(
                    int(issue['timestamp']))
                issue['date'] = dtime.strftime('%Y-%m-%d')
                issue['time'] = dtime.strftime('%H:%M:%S')

            with open(cachefile, 'w') as ofile:
                json.dump(self.loaded_issues, ofile)
        else:
            with open(cachefile) as jsonfile:
                self.loaded_issues = json.load(jsonfile)

        self.filtered_issues = self.loaded_issues[:]

    def add_filter(self, ftype, values):
        """ Set add_by property"""
        self.filters[ftype] = values

    def do_filters(self):
        """Filters issues with some filters"""

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

    # def download_image(self, token):
    #     """Download image"""
    #     img_filename = f"/tmp/{token}.png"

    #     if not os.path.exists(img_filename):
    #         print(f"Download image {token}")
    #         photo_url = f"{self.api_path}/get_photo.php?token={token}"
    #         print(photo_url)
    #         download_url_to_file(photo_url, img_filename)

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
