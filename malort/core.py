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
import random

from malort.stats import dict_generator, recur_dict
from malort.type_mappers import TypeMappers


def analyze(path, delimiter='\n'):

    stats = {}
    for count, blob in enumerate(dict_generator(path, delimiter)):
        recur_dict(blob, stats)

    return MalortStats(stats, count)


class MalortStats(TypeMappers):

    def __init__(self, stats, blob_count):
        """
        Wrapper for malort stats that can generate type maps and
        DataFrames

        Parameters
        ----------
        stats: dict
            Malort stats dict
        blob_count: int
            Number of JSON blobs read into result
        """
        self.stats = stats
        self.count = blob_count

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

        df_cols = ['key', 'count', 'type', 'mean', 'max', 'min',
                   'max_precision', 'max_scale', 'fixed_length', 'sample']

        if include_db_types:
            db_type_getters = [('redshift_types', self.get_redshift_types)]
            type_results = [(t[0], t[1]()) for t in db_type_getters]
            df_cols.extend([t[0] for t in db_type_getters])

        # Get the data into a to_dict-able format
        dictable = {}
        for i, (key, value) in enumerate(self.stats.items()):
            for ktype, stats in value.items():
                stats.update({'key': key, 'type': ktype})
                if include_db_types:
                    for name, result in type_results:
                        stats.update({name: result[key]})
                dictable[i] = stats

        df = pd.DataFrame.from_dict(dictable, 'index')

        return df.reindex_axis(df_cols, axis=1)
