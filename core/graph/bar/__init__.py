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
import pandas as pd
from PIL import Image, ImageColor, ImageDraw, ImageFont

import lib.image
import lib.issue
import lib.scope
from core.cmd import pass_context

CATEGORY = 2
DISTANCE = 100000

MAXPICTURES = 1000
MAX_SEARCH_ITERATION_RATIO = 10



@click.group()
def cli():
    """Bar graph"""

@click.option('-i', '--ifile', '--import', required=True, help="Import CSV")
@click.option('-o', '--output',  required=True, help='Output result filename',
              show_default=True)
@cli.command()
@pass_context
def generate(ctx,ifile,output):
    "Generate graph"

    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt


    df = pd.read_csv(ifile)

    palette = "RdBu"

    # COLOR Palette => https://seaborn.pydata.org/generated/seaborn.color_palette.html

    width=800
    height=600

    fig, ax = plt.subplots(figsize=(width/100.0,height/100.0))
    ax.set_title('Nombre observations par scope')

    ax1 = sns.barplot(ax=ax,y="scopeid",x="count",data=df,palette=palette)

    fig.savefig(output,bbox_inches='tight')

    plt.show()
