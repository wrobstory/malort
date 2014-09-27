# -*- coding: utf-8 -*-
"""
Malort Type Mappers
-------

Type mappings for Malort results. Can be extended for other database
types.
"""
from abc import abstractmethod


class AbstractMapper(object):

    @abstractmethod
    def booleans(self):
        pass

    @abstractmethod
    def strings(self):
        pass

    @abstractmethod
    def ints(self):
        pass

    @abstractmethod
    def floats(self):
        pass

    @abstractmethod
    def dates(self):
        pass


class RedshiftMapper(AbstractMapper):
    """Mapping of types/statistics to Redshift Column Types"""

    @staticmethod
    def booleans(stat):
        return "BOOLEAN"

    @staticmethod
    def strings(stat):
        trues = ['TRUE', 't', 'true', 'y', 'yes']
        falses = ['FALSE', 'f', 'false', 'n', 'no']
        matcher_bool = []
        for entry in stat['sample']:
            if entry in trues or entry in falses:
                matcher_bool.append(True)
            else:
                matcher_bool.append(False)
        if all(matcher_bool):
            return "BOOLEAN"
        else:
            if stat['min'] == stat['max'] == int(stat['mean']):
                return 'char({})'.format(stat['max'])
            elif stat['max'] > 65535:
                return 'Too large for any char column!'
            else:
                return 'varchar({})'.format(stat['max'])

    @staticmethod
    def ints(stat):
        if stat['min'] > -32768 and stat['max'] < 32767:
            return 'SMALLINT'
        elif stat['min'] > -2147483648 and stat['max'] < 2147483647:
            return 'INTEGER'
        else:
            return 'BIGINT'

    @staticmethod
    def floats(stat):
        if (stat['fixed_length'] and stat['max_precision'] <= 38
            and stat['max_scale'] <= 37):
            return 'decimal({}, {})'.format(stat['max_precision'],
                                            stat['max_scale'])
        else:
            if stat['max_precision'] <= 6:
                return 'REAL'
            else:
                return 'FLOAT'

    @staticmethod
    def dates(stat):
        return "TIMESTAMP"


class TypeMappers(object):

    def _get_types(self, mapper):
        """
        Given a dict of Malort results, map the statistics to given

        Parameters
        ----------
        stats: dict
            Dict of malort results
        mapper: malort.type_mapper
            Malort Type Mapper (RedshiftMapper, etc)
        """
        type_to_mapper = {
            'str': getattr(mapper, 'strings'),
            'int': getattr(mapper, 'ints'),
            'float': getattr(mapper, 'floats'),
            'bool': getattr(mapper, 'booleans'),
            'datetime': getattr(mapper, 'dates')
        }
        type_mapping = {}
        for key, value in self.stats.items():
            type_keys = list(value.keys())
            type_keys.remove('base_key')
            if len(type_keys) > 1:
                type_mapping[key] = 'Multiple types detected.'
            else:
                type_mapping[key] = type_to_mapper[type_keys[0]](
                    value[type_keys[0]]
                )
        return type_mapping

    def get_redshift_types(self):
        """
        Get Redshift-specific types for this Malort run.
        """
        return self._get_types(RedshiftMapper)
