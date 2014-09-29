# -*- coding: utf-8 -*-
"""
Malort Stats
-------

Functions to generate Malort stats

"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import decimal
import json
import os
from os.path import isfile, join, splitext
import random
import re


ISO8601 = re.compile(r"""^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]
                      \d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]
                      |0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|
                      2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]\d+(?!:))?)?(\17[0-5]
                      \d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)
                      ?)?)?$""", re.VERBOSE)


def catch_json_error(blob, filepath):
    """Wrapper to provide better error message for JSON reads"""
    try:
        parsed = json.loads(blob)
    except ValueError as e:
        raise ValueError("JSON error reading {}: {}!".format(filepath,
                                                             e.args[0]))

    return parsed

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
                        yield catch_json_error(row, filepath)
                else:
                    yield catch_json_error(fread.read(), filepath)

def get_new_mean(value, current_mean, count):
    """Given a value, current mean, and count, return new mean"""
    summed = current_mean * count
    return (summed + value)/(count + 1)

def updated_entry_stats(value, current_stats, parse_timestamps=True):
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

    # Python 2.7
    if value_type == 'unicode':
        value_type = 'str'

    # Datetimes
    if value_type == 'str' and parse_timestamps and ISO8601.match(value):
        value_type = 'datetime'

    new_stats = {}
    stats = current_stats.get(value_type, {})
    if value_type == 'str':
        val = len(value)
    else:
        val = value
    count = stats.get('count', 0)
    if value_type in ['str', 'int', 'float']:
        max_, min_, mean = (stats.get('max', val),
                            stats.get('min', val),
                            stats.get('mean', 0))

        new_stats['mean'] = round(get_new_mean(val, mean, count), 3)
        new_stats['max'] = val if max_ < val else max_
        new_stats['min'] = val if min_ > val else min_

        if value_type == 'str':
            sample = stats.get('sample', [])
            if len(sample) == 3:
                if random.randint(0, 1):
                    sample.pop(0)
                    sample.append(value)
            else:
                sample.append(value)
            new_stats['sample'] = sample

        elif value_type == 'float':
            dec_tup = decimal.Decimal(str(value)).as_tuple()
            vprec, vscale = len(dec_tup.digits), abs(dec_tup.exponent)
            mxprec = stats.get('max_precision', vprec)
            mxscale = stats.get('max_scale', vscale)
            if mxprec != vprec or mxscale != vscale:
                new_stats['fixed_length'] = False
            else:
                new_stats['fixed_length'] = True
            new_stats['max_precision'] = vprec if mxprec < vprec else mxprec
            new_stats['max_scale'] = vscale if mxscale < vscale else mxscale

    new_stats['count'] = count + 1

    return value_type, new_stats


def recur_dict(value, stats, parent=None, **kwargs):
    """
    Recurse through a dict `value` and update `stats` for each field.
    Can handle nested dicts and lists of dicts, but will raise exception
    for list of values

    Parameters
    ----------
    value: dict
    stats: dict
    parent: string, default None
        Parent key to get key nesting depth.
    kwargs: Options for update_entry_stats
    """

    parent = parent or ''

    if isinstance(value, dict):
        for k, v in value.items():
            parent_path = '.'.join([parent, k]) if parent != '' else k
            if isinstance(v, (list, dict)):
                recur_dict(v, stats, parent_path)
            else:
                if parent_path not in stats:
                    stats[parent_path] = {}
                current_stats = stats.get(parent_path)
                value_type, new_stats = updated_entry_stats(v, current_stats,
                                                            **kwargs)
                current_stats[value_type] = new_stats
                current_stats['base_key'] = k

    elif isinstance(value, list):
        for v in value:
            if isinstance(v, (list, dict)):
                recur_dict(v, stats, parent)
            else:
                raise ValueError('List of values found. Malort can only pro'
                                 'cess key: value pairs!')

    return stats
