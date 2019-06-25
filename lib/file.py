#!/usr/bin/env python
# -*- coding: utf-8 -*-


def write_content_to_file(content, filename):
    with open(filename, 'w') as ofile:
        ofile.write(content)
