#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import inspect
import json
import os
import time

import geopy
import geopy.distance

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
        self.max_distance = 50
        self.near_issues = []
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

    def set_maxdistance(self, max_distance):
        """Define max_distance property"""
        self.max_distance = max_distance

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
                issue['time'] = dtime.strftime('%H:%M')

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

        # Search issue near items
        self.near_issues = self.search_token(self.filters['near'])

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

    def filter_by_near(self, item):
        """Add by near filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')
        if not self.filters[ftype]:
            return True

        lat = float(item['coordinates_lat'])
        lon = float(item['coordinates_lon'])
        geopoint_issue = geopy.Point(lat, lon)
        for near_issue in self.near_issues:
            lat = float(near_issue['coordinates_lat'])
            lon = float(near_issue['coordinates_lon'])
            geopoint_search = geopy.Point(lat, lon)

            distance = geopy.distance.distance(
                geopoint_issue, geopoint_search).m

            if distance < self.max_distance:
                return True

        return False

    def search_token(self, tokens):
        """Find tokens"""
        find_tokens = []
        for item in self.loaded_issues:
            if item['token'] in tokens:
                find_tokens.append(item)

        return find_tokens
