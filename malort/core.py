# -*- coding: utf-8 -*-
"""
Malort
-------

JSON -> Postgres Column types

"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from collections import defaultdict
import json
import os
from os.path import isfile, join, splitext
import random
import time

from malort.stats import recur_dict, dict_generator
from malort.type_mappers import TypeMappers


def analyze(path, delimiter='\n', parse_timestamps=True):
    """
    Analyze a given directory of either .json or flat text files
    with delimited JSON to get relevant key statistics.

    Parameters
    ----------
    path: string
        Path to directory
    delimiter: string, default newline
        For flat text files, the JSON blob delimiter
    parse_timestamps: boolean, default True
        If True, will attempt to regex match ISO8601 formatted parse_timestamps
    """

    stats = {}

    start_time = time.time()
    for count, blob in enumerate(dict_generator(path, delimiter)):
        recur_dict(blob, stats, parse_timestamps=parse_timestamps)

    elapsed = time.time() - start_time
    print('Malort run finished: {} JSON blobs analyzed in {} seconds.'
          .format(count, elapsed))
    return MalortResult(stats, count, elapsed)


class MalortResult(TypeMappers):

    def __init__(self, stats, blob_count, execution_time=None):
        """
        Wrapper for malort stats that can generate type maps and
        DataFrames

        Parameters
        ----------
        stats: dict
            Malort stats dict
        blob_count: int
            Number of JSON blobs read into result
        execution_time: float, default None
            Execution time in seconds
        """
        self.stats = stats
        self.count = blob_count
        self.execution_time = execution_time

    def get_conflicting_types(self):
        """Return only the stats where there are multiple types detected"""
        conflicted = {}
        for k, v in self.stats.items():
            type_keys = list(v.keys())
            type_keys.remove('base_key')
            if len(type_keys) > 1:
                conflicted[k] = v

        return conflicted

    def to_dataframe(self, include_db_types=True):
        """
        Export stats dict to a Pandas DataFrame

        Parameters
        ----------
        include_db_types: boolean, default True
            Include database type inference in DataFrame
        """
        import pandas as pd

        df_cols = ['key', 'base_key', 'count', 'type', 'mean', 'max', 'min',
                   'max_precision', 'max_scale', 'fixed_length', 'sample']

        if include_db_types:
            db_type_getters = [('redshift_types', self.get_redshift_types)]
            type_results = [(t[0], t[1]()) for t in db_type_getters]
            df_cols.extend([t[0] for t in db_type_getters])

        # Get the data into a to_dict-able format
        dictable = defaultdict(dict)
        for i, (key, value) in enumerate(self.stats.items()):

            dictable[i]['base_key'] = value['base_key']
            dictable[i]['key'] = key

            for ktype, stats in value.items():

                if ktype not in ['base_key']:
                    dictable[i]['type'] = ktype

                    for stat, statvalue in stats.items():
                        dictable[i][stat] = statvalue

                if include_db_types:
                    for name, result in type_results:
                        dictable[i].update({name: result[key]})

        df = pd.DataFrame.from_dict(dictable, 'index')

        return df.reindex_axis(df_cols, axis=1)

    def gen_redshift_jsonpaths(self, filepath=None):
        """Generate Redshift jsonpath file for results

        Parameters
        ----------
        filepath: str, default None
            If path is provided, will write jsonpaths to file.
        """
        jsonpaths = {"jsonpaths": []}
        for k in self.stats.keys():
            parts = k.split('.')
            path = '$'
            for p in parts:
                path = path + "['{}']".format(p)
            jsonpaths['jsonpaths'].append(path)
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(jsonpaths, f, sort_keys=True, indent=4)
        else:
            return jsonpaths
