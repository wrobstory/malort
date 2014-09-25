# -*- coding: utf-8 -*-
"""
Malort Type Mappers
-------

Type mappings for Malort results. Can be extended for other database
types.
"""

class RedshiftMapper(object):

    def strings(stat):
        if stat['min'] == stat['max'] == int(stat['mean']):
            return "char({})".format(stat['max'])
        elif stat['max'] > 65535:
            return "Too large for any char column!"
        else:
            return "varchar({})".format(stat['max'])

    def ints(stat):
        if stat['min'] > -32768 and stat['max'] < 32767:
            return "SMALLINT"
        elif stat['min'] > -2147483648 and stat['max'] < 2147483647:
            return "INTEGER"
        else:
            return "BIGINT"

    def floats(stat):
        pass


class TypeMappers(object):

    def get_redshift_types(self):
        """
        Given a dict of Malort results, map the statistics to Redshift types.

        Parameters
        ----------
        stats: dict
            Dict of malort results
        """

        type_mapping = {}
        # for key, value in self.stats.items():
