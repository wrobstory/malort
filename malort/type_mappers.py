# -*- coding: utf-8 -*-
"""
Malort Type Mappers
-------

Type mappings for Malort results. Can be extended for other database
types.
"""

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
