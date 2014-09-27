# -*- coding: utf-8 -*-
"""
Malort Tests

Test Runner: PyTest

Notes:
* Expected values for string samples are any values that the sample
could contain, not the exact values.

"""
import os
import unittest

import pytest

import malort as mt
from malort.test_helpers import TestHelpers, TEST_FILES_1, TEST_FILES_2


class TestDictGenerator(TestHelpers):

    def test_json_files_newline(self):
        gen = mt.stats.dict_generator(TEST_FILES_1)
        self.assertEquals(len([d for d in gen]), 4)

    def test_json_files_pipe(self):
        gen = mt.stats.dict_generator(TEST_FILES_2, '|')
        self.assertEquals(len([d for d in gen]), 4)


class TestUpdateEntryStats(TestHelpers):

    def test_stats_str(self):
        vtype1, update_1 = mt.stats.update_entry_stats('Foooo', {})
        print(update_1)
        self.assertEquals(update_1,
                          {'count': 1, 'mean': 5.0, 'max': 5,
                           'min': 5, 'sample': ['Foooo']})

        vtype2, update_2 = mt.stats.update_entry_stats('Foooo',
                                                      {'str': update_1})
        self.assertEquals(update_2,
                          {'count': 2, 'mean': 5.0, 'max': 5,
                           'min': 5, 'sample': ['Foooo', 'Foooo']})

        vtype3, update_3 = mt.stats.update_entry_stats('Foo', {'str': update_2})
        self.assertEquals(update_3,
                          {'count': 3, 'mean': 4.333, 'max': 5,
                           'min': 3, 'sample': ['Foooo', 'Foooo', 'Foo']})

        vtype4, update_4 = mt.stats.update_entry_stats('2014-08-07 10:00:00',
                                                       {})
        self.assertEquals(update_4, {'count': 1})

        vtype4, update_4 = mt.stats.update_entry_stats('2014-08-07', {})
        self.assertEquals(update_4, {'count': 1})

        for v in [vtype1, vtype2, vtype3]:
            self.assertEquals(v, 'str')

    def test_stats_bool(self):
        vtype1, update_1 = mt.stats.update_entry_stats(True, {})
        self.assertEquals(update_1, {'count': 1})

        vtype2, update_2 = mt.stats.update_entry_stats(False,
                                                       {'bool': update_1})
        self.assertEquals(update_2, {'count': 2})

        for v in [vtype1, vtype2]:
            self.assertEquals(v, 'bool')

    def test_stats_number(self):
        vtype1, update_1 = mt.stats.update_entry_stats(1, {})
        self.assertEquals(update_1,
                          {'count': 1, 'mean': 1.0, 'max': 1,
                           'min': 1})

        vtype2, update_2 = mt.stats.update_entry_stats(2.0, {'int': update_1})
        self.assertEquals(update_2,
                          {'count': 1, 'mean': 2.0, 'max': 2.0,
                           'min': 2.0, 'max_precision': 2,
                           'max_scale': 1, 'fixed_length': True})

        vtype3, update_3 = mt.stats.update_entry_stats(2, {'int': update_1,
                                                          'float': update_2})
        self.assertEquals(update_3,
                          {'count': 2, 'mean': 1.5, 'max': 2,
                           'min': 1})

        vtype4, update_4 = mt.stats.update_entry_stats(4.555,
                                                      {'int': update_3,
                                                       'float': update_2})
        self.assertEquals(update_4,
                          {'count': 2, 'mean': 3.277, 'max': 4.555,
                           'min': 2.0, 'max_precision': 4,
                           'max_scale': 3, 'fixed_length': False})

        for v in [vtype1, vtype3]:
            self.assertEquals(v, 'int')
        for v in [vtype2, vtype4]:
            self.assertEquals(v, 'float')


class TestRecurDict(TestHelpers):

    def test_recur_simple(self):
        simple1 = {'key1': 1, 'key2': 'Foo', 'key3': 4.0, 'key4': True}
        expected = {
            'key1': {'int': {'count': 1, 'max': 1, 'mean': 1.0, 'min': 1},
                     'base_key': 'key1'},
            'key2': {'str': {'count': 1, 'max': 3, 'mean': 3.0, 'min': 3,
                             'sample': ['Foo']},
                     'base_key': 'key2'},
            'key3': {'float': {'count': 1, 'max': 4.0, 'mean': 4.0,
                               'min': 4.0, 'max_precision': 2,
                               'max_scale': 1, 'fixed_length': True},
                     'base_key': 'key3'},
            'key4': {'bool': {'count': 1}, 'base_key': 'key4'}
        }

        stats = mt.stats.recur_dict(simple1, {})
        self.assertDictEqual(stats, expected)

        updated_stats = mt.stats.recur_dict({'key1': 2}, stats)
        self.assertDictEqual(updated_stats['key1'],
                             {'int': {'count': 2, 'max': 2, 'mean': 1.5,
                                      'min': 1}, 'base_key': 'key1'})


    def test_recur_depth_one(self):
        depth_one = {
            'key1': 1, 'key2': 'Foo', 'key3': 4.0, 'key4': True,
            'key5': {
                'key1': 2, 'key2': 'Foooo', 'key3': 8.0, 'key4': False,
            }
        }
        expected = {'key1': {'base_key': 'key1',
                             'int': {'count': 1, 'max': 1, 'mean': 1.0,
                                     'min': 1}},
                    'key2': {'base_key': 'key2',
                             'str': {'count': 1,
                                     'max': 3,
                                     'mean': 3.0,
                                     'min': 3,
                                     'sample': ['Foo']}},
                    'key3': {'base_key': 'key3',
                             'float': {'count': 1,
                                       'fixed_length': True,
                                       'max': 4.0,
                                       'max_precision': 2,
                                       'max_scale': 1,
                                       'mean': 4.0,
                                       'min': 4.0}},
                    'key4': {'base_key': 'key4', 'bool': {'count': 1}},
                    'key5.key1': {'base_key': 'key1',
                                  'int': {'count': 1, 'max': 2, 'mean': 2.0,
                                          'min': 2}},
                    'key5.key2': {'base_key': 'key2',
                                  'str': {'count': 1,
                                          'max': 5,
                                          'mean': 5.0,
                                          'min': 5,
                                          'sample': ['Foooo']}},
                    'key5.key3': {'base_key': 'key3',
                                  'float': {'count': 1,
                                            'fixed_length': True,
                                            'max': 8.0,
                                            'max_precision': 2,
                                            'max_scale': 1,
                                            'mean': 8.0,
                                            'min': 8.0}},
                    'key5.key4': {'base_key': 'key4', 'bool': {'count': 1}}}

        stats = mt.stats.recur_dict(depth_one, {})
        self.assert_stats(stats, expected)

    @property
    def depth_two_expected(self):
        return {'key1': {'base_key': 'key1',
                         'int': {'count': 1, 'max': 1, 'mean': 1.0, 'min': 1}},
                'key2': {'base_key': 'key2',
                         'str': {'count': 1,
                                 'max': 3,
                                 'mean': 3.0,
                                 'min': 3,
                                 'sample': ['Foo']}},
                'key3': {'base_key': 'key3',
                         'float': {'count': 1,
                                   'fixed_length': True,
                                   'max': 4.0,
                                   'max_precision': 2,
                                   'max_scale': 1,
                                   'mean': 4.0,
                                   'min': 4.0}},
                'key4': {'base_key': 'key4', 'bool': {'count': 1}},
                'key5.key1': {'base_key': 'key1',
                              'int': {'count': 1, 'max': 2, 'mean': 2.0,
                                      'min': 2}},
                'key5.key2': {'base_key': 'key2',
                              'str': {'count': 1,
                                      'max': 5,
                                      'mean': 5.0,
                                      'min': 5,
                                      'sample': ['Foooo']}},
                'key5.key3': {'base_key': 'key3',
                              'float': {'count': 1,
                                        'fixed_length': True,
                                        'max': 8.0,
                                        'max_precision': 2,
                                        'max_scale': 1,
                                        'mean': 8.0,
                                        'min': 8.0}},
                'key5.key4': {'base_key': 'key4', 'bool': {'count': 1}},
                'key5.key6.key1': {'base_key': 'key1',
                                   'str': {'count': 1,
                                           'max': 3,
                                           'mean': 3.0,
                                           'min': 3,
                                           'sample': ['Foo']}},
                'key5.key6.key2': {'base_key': 'key2',
                                   'float': {'count': 1,
                                             'fixed_length': True,
                                             'max': 3.0,
                                             'max_precision': 2,
                                             'max_scale': 1,
                                             'mean': 3.0,
                                             'min': 3.0}},
                'key5.key6.key3': {'base_key': 'key3',
                                   'float': {'count': 1,
                                             'fixed_length': True,
                                             'max': 2.0,
                                             'max_precision': 2,
                                             'max_scale': 1,
                                             'mean': 2.0,
                                             'min': 2.0}},
                'key5.key6.key4': {'base_key': 'key4', 'bool': {'count': 1}}}

    def test_recur_depth_two(self):
        depth_two = {
            'key1': 1, 'key2': 'Foo', 'key3': 4.0, 'key4': True,
            'key5': {
                'key1': 2, 'key2': 'Foooo', 'key3': 8.0, 'key4': False,
                'key6': {
                    'key1': "Foo", 'key2': 3.0, 'key3': 2.0, 'key4': False
                }
            }
        }

        stats = mt.stats.recur_dict(depth_two, {})
        self.assert_stats(stats, self.depth_two_expected)

    def test_recur_with_array(self):
        with_list = {
            'key1': 1, 'key2': 'Foo', 'key3': 4.0, 'key4': True,
            'key5': [{'key1': 2, 'key2': 'Foooo', 'key3': 8.0, 'key4': False},
                     {'key6': {'key1': "Foo", 'key2': 3.0, 'key3': 2.0,
                               'key4': False}}
                ]
        }

        stats = mt.stats.recur_dict(with_list, {})
        self.assert_stats(stats, self.depth_two_expected)

    def test_raises_with_list_of_values(self):
        with_values = {
            'key1': 'Foo',
            'key2': ['Foo', 'Bar']
        }

        with pytest.raises(ValueError):
            mt.stats.recur_dict(with_values, {})
