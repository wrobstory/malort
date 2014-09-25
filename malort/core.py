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


__all__ = ('dict_generator', 'update_entry_stats')


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

value = {
    "str": {'count': 5, 'avg_len': 6},
    "int": {'max': 67, 'min': 0, 'mean': 5, 'count': 8},
    "float": {'max': 6.7, 'min': -1.3, 'count': 6},
    "boolean": {'count': 6}
}


def get_new_mean(value, current_mean, count):
    """Given a value, current mean, and count, return new mean"""
    summed = current_mean * count
    return (summed + value)/(count + 1)


def update_entry_stats(value, current_stats):
    """
    Given a value and a dict of current statistics, return a dict of new
    statistics for the given value type. Values for str reference their len.

    Ex:
    current_stats = {
        "str": {'count': 2, 'max': 2, 'min': 1, 'mean': 1.5},
        "int": {'count': 1, 'max': 5, 'min': 5, 'mean': 5},
    }
    update_entry_stats(10, current_stats)
    {'count': 2, 'max': 10, 'min': 5, 'mean': 7.5}

    Parameters
    ----------
    value: str, int, float, boolean
    current_stats: Dict, see Example
    """
    value_type = type(value).__name__
    new_stats = {}
    stats = current_stats.get(value_type, {})
    if value_type == 'str':
        value = len(value)
    count = stats.get('count', 0)
    if value_type in ['str', 'int', 'float']:
        max_, min_, mean = (stats.get('max', value),
                            stats.get('min', value),
                            stats.get('mean', 0))

        new_stats['mean'] = round(get_new_mean(value, mean, count), 3)
        new_stats['max'] = value if max_ < value else max_
        new_stats['min'] = value if min_ > value else min_
    new_stats['count'] = count + 1

    return new_stats
