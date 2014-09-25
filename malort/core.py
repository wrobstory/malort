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
    for blob in dict_generator(path, delimiter):
        recur_dict(blob, stats)

    return MalortStats(stats)


class MalortStats(TypeMappers):

    def __init__(self, stats):
        """
        Wrapper for malort stats that can generate type maps and
        DataFrames

        Parameters
        ----------
        stats: dict
            Malort stats dict
        """
        self.stats = stats

    def get_conflicting_types(self):
        """Return only the stats where there are multiple types detected"""
        conflicted = {}
        for k, v in self.stats.items():
            if len(v.keys()) > 1:
                conflicted[k] = v

        return conflicted
