#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import inspect
import json
import os
import time

import geopy
import geopy.distance
import pandas as pd

import lib.net
import lib.scope
import lib.image

from tabulate import tabulate

# Set pandas options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def agg_count(df):
    return df.count()


def agg_sum(df):
    return df.sum()


def agg_range(df):
    return f'{df.min()} - {df.max()}'


class Issues():
    """
    Issues class
    """

    def __init__(self):
        self.debug = False
        self.scopes_list = []
        self.scopes = []
        self.sortby = ""
        self.groupby = ""
        self.groupfunc = ""
        self.populate = ""
        self.having = ""
        self.reverse = False
        self.verbose = True
        self.head = 0
        self.tail = 0
        self.wantfields = []
        self.showedfields = []
        self.max_distance = 50
        self.near_issues = []
        self.loaded_all_issues = {}
        self.filtered_issues = {}
        self.field_names = []
        self.no_cache = False
        self.filters = {}

    def set_debug(self, debug):
        """Set debug proprety"""
        self.debug = debug

    def set_nocache(self, no_cache):
        """Define nocache property"""
        self.no_cache = no_cache

    def set_scopes(self, scopes):
        """Define scope property"""
        self.scopes_list = lib.scope.get_scope_list()

        # Set scopes or get all scopes
        if len(scopes) == 1 and scopes[0].lower() == "all":
            self.scopes = self.scopes_list.index.to_list()
        else:
            self.scopes = list(scopes)

    def set_maxdistance(self, max_distance):
        """Define max_distance property"""
        self.max_distance = max_distance

    def set_sortby(self, sortby):
        """Define max_distance property"""
        self.sortby = sortby

    def set_groupby(self, groupby):
        """Define max_distance property"""
        self.groupby = groupby

    def set_groupfunction(self, groupfunc):
        """Define max_distance property"""
        self.groupfunc = groupfunc

    def set_populate(self, populate):
        """Define populate actions"""
        self.populate = populate

    def set_having(self, having):
        """Define max_distance property"""
        self.having = having

    def set_reverse(self, reverse):
        """Define max_distance property"""
        self.reverse = reverse

    def set_head(self, head):
        """Define max_distance property"""
        self.head = head

    def set_tail(self, tail):
        """Define max_distance property"""
        self.tail = tail

    def set_fields(self, fields):
        """Define fields table"""
        self.wantfields = fields

    def set_verbose(self, verbose):
        """Define fields table"""
        self.verbose = verbose

    def get_filtered_issues(self):
        """Get filter issues(add_filter)"""

        # Init
        filtered = self.filtered_issues.copy()

        # aggragation in group
        if self.groupby:
            filtered = filtered.groupby(list(self.groupby.split(",")))
            if self.verbose:
                print(f"Group by: {len(filtered)}")

            # Aggregate functions
            if self.groupfunc:
                groupfuncs = self.groupfunc.split(',')

                # First pass
                mydict = {}
                for groupfunc in groupfuncs:
                    column, func, name = groupfunc.split(':')

                    if '%' not in func:
                        mydict[name] = (column, eval(f'agg_{func}'))

                filtered = filtered.agg(**mydict)

                # Second pass
                mydict = {}
                for groupfunc in groupfuncs:
                    column, func, name = groupfunc.split(':')

                    if '%' in func:
                        filtered[name] = filtered[column] / \
                            filtered[column].sum() * 100
                        filtered[name] = filtered[name].round(2)

                if self.having:
                    havings = self.having.split(',')
                    for havingparam in havings:
                        column, having = havingparam.split(':')

                        filtered = filtered[eval(
                            f"filtered['{column}'] {having}")]

                    if self.verbose:
                        print(f"Having: {len(filtered)}")

            # Only use groupby
            else:
                if self.having:
                    havings = self.having.split(',')
                    for havingparam in havings:
                        column, func, having = havingparam.split(':')

                        filtered = filtered.filter(
                            lambda x: eval(f"x['{column}'].{func}() {having}"))

                    if self.verbose:
                        print(f"Having: {len(filtered)}")

                else:
                    filtered = filtered.filter(
                        lambda x: True)

        # Sort
        if self.sortby:
            filtered = filtered.sort_values(
                self.sortby.split(','), ascending=(self.reverse == False))

        if self.head > 0:
            filtered = filtered.head(self.head)

            if self.verbose:
                print(f"Head: {len(filtered)}")

        if self.tail > 0:
            filtered = filtered.tail(self.tail)

            if self.verbose:
                print(f"Tail: {len(filtered)}")

        return filtered

    def load_all_issues(self):
        """Get all issues from scope"""

        # Get scopes informations
        scopesinfo = self.scopes_list.loc[self.scopes]
        scopes_idx = (scopesinfo.index.tolist())
        scope_title = "-".join(sorted(scopes_idx))

        cachefile = f'/tmp/issues_{scope_title}.csv'
        df = None
        if self.no_cache or not os.path.exists(cachefile):
            issues = {}
            for rowscope in scopesinfo.itertuples():
                scopeid = rowscope.Index
                issue_url = f"{rowscope.api_path}/get_issues.php"
                data = lib.net.get_url_content(issue_url)
                loaded_issues = json.loads(data)

                for issue in loaded_issues:
                    token = issue['token']
                    issues[token] = issue
                    issues[token]['scopeid'] = scopeid
                    # del issues[token]['token']

                    issues[token]['timestamp'] = float(issue['time'])
                    dtime = datetime.datetime.fromtimestamp(
                        int(issues[token]['timestamp']))
                    issue['date'] = dtime.strftime('%Y-%m-%d')
                    issue['month'] = dtime.strftime('%B')
                    issue['monthidx'] = dtime.strftime('%m')
                    issue['weeknumber'] = dtime.strftime('%V')
                    issue['weekdayidx'] = dtime.strftime('%w')
                    issue['weekday'] = dtime.strftime('%A')
                    issue['year'] = dtime.strftime('%Y')
                    issue['time'] = dtime.strftime('%H:%M')
                    issue['hour'] = dtime.strftime('%H:00')

                    # Time
                    timename = ['nuit', 'matin', 'après-midi', 'soirée']
                    hour = int(dtime.strftime('%H'))
                    idx = int(hour/6)
                    issue['timeofdayidx'] = idx
                    issue['timeofday'] = timename[idx]

                    # Compute dhash
                    if 'image' in self.populate:
                        try:
                            lib.image.download_vigilo_image(
                                scopeid, token, rowscope.api_path)

                            img_filename = f"cache/{scopeid}_{token}.png"
                            issue['img_dhash'] = lib.image.compute_dhash(
                                img_filename)
                        except:
                            pass

            # Convert to pandas dataframe
            df = pd.DataFrame.from_dict(issues, orient='index')
            df.index = range(len(df))

            # Merge issues and scopes
            df = df.merge(scopesinfo, left_on='scopeid',
                          right_on='scopeid')

            # Save to csv
            df.to_csv(cachefile, index=None)

        else:
            df = pd.read_csv(filepath_or_buffer=cachefile, index_col="token")

        df = df.reindex(sorted(df.columns), axis=1)

        self.loaded_all_issues = df

        if self.verbose:
            print(f"Loaded issues: {len(df)}")

        return df

    def import_csv(self, filename):
        """Import CSV datas"""
        self.loaded_all_issues = pd.read_csv(
            filepath_or_buffer=filename)

        self.loaded_all_issues = self.loaded_all_issues.reset_index(drop=True)

    def add_filter(self, ftype, values):
        """ Set add_by property"""
        self.filters[ftype] = values

    def do_filters(self):
        """Filters issues with some filters"""

        # Search issue near items
        scopeid = -1
        filtered_issues = self.loaded_all_issues

        for ftype in self.filters:
            if len(self.filters[ftype]) > 0:
                filtered_issues = getattr(self, f"filter_by_{ftype}")(
                    scopeid, filtered_issues)

                if self.verbose:
                    print(f"filter_by_{ftype} : {len(filtered_issues)}")

        self.filtered_issues = filtered_issues

    def filter_by_address(self, scopeid, filtered_issues):
        """Add by string filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')

        # Init mask
        mask = filtered_issues['address'] == ""

        # Search contain text
        for searchtext in self.filters[ftype]:
            containoperator = searchtext.find('!') == -1
            if not containoperator:
                continue

            mask = mask | filtered_issues.address.str.contains(
                pat=searchtext, case=False)

        # Search not contain text
        for searchtext in self.filters[ftype]:
            notcontainoperator = searchtext.find('!') == 0
            if not notcontainoperator:
                continue

            searchtext = searchtext[1:]
            mask = mask & ~filtered_issues.address.str.contains(
                pat=searchtext, case=False)

        return filtered_issues[mask]

    def filter_by_string(self, scopeid, filtered_issues):
        """Add by string filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')

        # Init mask
        mask = filtered_issues['comment'] is None

        # Search string
        for searchtext in self.filters[ftype]:
            mask = mask | filtered_issues.comment.str.contains(
                pat=searchtext, case=False) \
                | filtered_issues.explanation.str.contains(pat=searchtext, case=False)

        return filtered_issues[mask]

    def filter_by_category(self, scopeid, filtered_issues):
        """Add by category filter"""

        ftype = inspect.stack()[0][3].replace('filter_by_', '')
        mask = filtered_issues.categorie.isin(self.filters[ftype])

        return filtered_issues[mask]

    def filter_by_date(self, scopeid, filtered_issues):
        """Add by date filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')

        # Init mask
        mask = filtered_issues['timestamp'] > 0

        for dates in self.filters[ftype]:
            start, end = dates

            tstart = time.mktime(datetime.datetime.strptime(
                start, "%Y-%m-%d %H:%M:%S").timetuple())
            tend = time.mktime(datetime.datetime.strptime(
                end, "%Y-%m-%d %H:%M:%S").timetuple())

            mask = mask & ((filtered_issues.timestamp >=
                            tstart) & (filtered_issues.timestamp <= tend))

        return filtered_issues[mask]

    def filter_by_token(self, scopeid, filtered_issues):
        """Add by token filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')

        return filtered_issues.loc[list(self.filters[ftype]), :]

    def filter_by_ignore(self, scopeid, filtered_issues):
        """Add by token filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')

        ignore_idx = filtered_issues.index.isin(list(self.filters[ftype]))
        return filtered_issues.loc[~ignore_idx, :]

    def filter_by_near(self, scopeid, filtered_issues):
        """Add by near filter"""
        ftype = inspect.stack()[0][3].replace('filter_by_', '')
        if not self.filters[ftype]:
            return filtered_issues

        local_issues = filtered_issues[:]
        near_issues = local_issues.loc[self.filters[ftype], :]

        # Init mask
        mask = local_issues['categorie'] is not None

        # Search near issues
        for index_near, near_issue in near_issues.iterrows():
            lat = float(near_issue.coordinates_lat)
            lon = float(near_issue.coordinates_lon)
            geopoint_near = geopy.Point(lat, lon)

            near_column_name = f'near_{index_near}'

            local_issues[near_column_name] = local_issues.apply(lambda row: geopy.distance.distance(
                geopoint_near, geopy.Point(row['coordinates_lat'], row['coordinates_lon'])).m, axis=1)
            mask = mask & (local_issues[near_column_name] < self.max_distance)

        return local_issues[mask]

    def compute_showedfields(self):
        columns = list(self.get_filtered_issues().reset_index().columns)

        # Show all fields
        if self.wantfields.lower() == 'all':
            selected_fields = columns
            self.showedfields = selected_fields
        else:
            # Show selected fields
            self.showedfields = self.wantfields.lower().split(',')

    def output(self, filename=""):
        df_issues = self.get_filtered_issues()
        df_issues = df_issues.reset_index()

        self.compute_showedfields()

        df_issues = df_issues[self.showedfields]

        if filename:
            df_issues.to_csv(filename, index=None)
            print(f"Exported successively to {filename} file")
        else:
            self.show(df_issues)

    def show(self, df_issues):
        print(tabulate(df_issues, headers='keys',
                       tablefmt="orgtbl", showindex=False))
        # floatfmt='.2f'

    def get_field_names(self):
        """Return fields list"""
        return sorted(list(self.loaded_all_issues.columns))
