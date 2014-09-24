# -*- coding: utf-8 -*-
"""
Malort
-------

JSON -> Postgres Column types

"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import json
import os
from os.path import isfile, join, splitext


__all__ = ('dict_generator')


def dict_generator(path, delimiter='\n'):
    """
    Given a directory path, return a generator that will return a dict for each
    JSON blob.

    If the directory contains .json, it will yield one dict per file. If a
    delimiter is specified, it will split on the delimiter and return one dict
    per json blob

    Parameters
    ----------
    path: string
        Directory path
    delimiter: string, default None
        Delimiter for text files with delimited JSON
    """
    for f in os.listdir(path):
        filepath = join(path, f)
        if isfile(filepath):
            with open(filepath, 'r') as fread:
                if splitext(f)[1] != '.json':
                    blob = fread.read()
                    split = blob.split(delimiter)
                    for row in split:
                        yield json.loads(row)
                else:
                    yield json.loads(fread.read())

