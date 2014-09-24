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
    .json file and `delimiter` separated blob in a text file.

    Ex: In directory 'files' you have the following
    foo.json: '{"foo": 1}'
    bar.txt: '{"bar": 2}|{"baz": 3}'

    malort.core.dict_generator('files', '|') will generate the dicts
    {'foo': 1}, {'bar': 2}, and {'baz': 3}

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

