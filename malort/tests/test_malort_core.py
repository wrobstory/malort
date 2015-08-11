# -*- coding: utf-8 -*-
"""
Malort Core Tests

Test Runner: PyTest

Notes:
* Expected values for string samples are any values that the sample
could contain, not the exact values.

"""
import os

import malort as mt
from malort.test_helpers import (TestHelpers, TEST_FILES_1, TEST_FILES_2,
                                 TEST_FILES_3, TEST_FILES_4)


class TestCore(TestHelpers):

    expected_1_and_2 = {
        'charfield': {'str': {'count': 4, 'max': 11, 'mean': 11.0,
                              'min': 11, 'sample': ['fixedlength']},
                      'base_key': 'charfield'},
        'floatfield': {'float': {'count': 4, 'max': 10.8392, 'mean': 5.244,
                                 'min': 2.345, 'max_precision': 6,
                                 'max_scale': 4, 'fixed_length': False},
                       'base_key': 'floatfield'},
        'intfield': {'int': {'count': 4, 'max': 20, 'mean': 12.5,
                             'min': 5},
                     'base_key': 'intfield'},
        'varcharfield': {'str': {'count': 4, 'max': 12, 'mean': 7.5,
                                 'min': 3,
                                 'sample': ['var', 'varyin', 'varyingle',
                                            'varyinglengt']},
                         'base_key': 'varcharfield'},
        'datefield': {'datetime': {'count': 4}, 'base_key': 'datefield'},
    }

    def test_files_1(self):
        mtresult = mt.analyze(TEST_FILES_1)
        self.assertEqual(mtresult.count, 4)
        self.assert_stats(mtresult.stats, self.expected_1_and_2)
        self.assertDictEqual(mtresult.get_conflicting_types(), {})

    def test_files_2(self):
        mtresult = mt.analyze(TEST_FILES_2)
        self.assertEqual(mtresult.count, 4)
        self.assert_stats(mtresult.stats, self.expected_1_and_2)
        self.assertDictEqual(mtresult.get_conflicting_types(), {})

    def test_files_3(self):
        mtresult = mt.analyze(TEST_FILES_3)
        expected = {'baz.qux': {'base_key': 'qux',
                                'str': {'count': 3,
                                        'max': 5,
                                        'mean': 3.667,
                                        'min': 3,
                                        'sample': ['One', 'Two', 'Three']}},
                    'foo.bar': {'base_key': 'bar',
                                'int': {'count': 3, 'max': 30, 'mean': 20.0,
                                        'min': 10}},
                    'qux': {'base_key': 'qux', 'bool': {'count': 1}}}
        self.assert_stats(mtresult.stats, expected)
        self.assertEqual(mtresult.count, 3)
        self.assert_stats(mtresult.get_conflicting_types(), expected)

    def test_files_4(self):
        mtresult = mt.analyze(TEST_FILES_4)
        expected = {
            'bar': {'bool': {'count': 1},
                    'float': {'count': 2, 'max': 4.0, 'mean': 3.0, 'min': 2.0,
                              'max_precision': 2, 'max_scale': 1,
                              'fixed_length': True},
                    'str': {'count': 1, 'max': 3, 'mean': 3.0, 'min': 3,
                            'sample': ['bar']},
                    'base_key': 'bar'},
            'baz': {'int': {'count': 2, 'max': 2, 'mean': 1.5, 'min': 1},
                    'str': {'count': 2, 'max': 5, 'mean': 5.0, 'min': 5,
                            'sample': ['fixed']},
                    'base_key': 'baz'},
            'foo': {'int': {'count': 2, 'max': 1000, 'mean': 505.0, 'min': 10},
                    'str': {'count': 2, 'max': 3, 'mean': 3.0, 'min': 3,
                            'sample': ['foo']},
                    'base_key': 'foo'},
            'qux': {'int': {'count': 1, 'max': 10, 'mean': 10.0, 'min': 10},
                    'str': {'count': 3, 'max': 9, 'mean': 6.0, 'min': 3,
                            'sample': ['var', 'varyin', 'varyingle']},
                    'base_key': 'qux'}
        }

        self.assert_stats(mtresult.stats, expected)
        self.assertEqual(mtresult.count, 4)
        self.assert_stats(mtresult.get_conflicting_types(), expected)

    def test_gen_redshift_jsonpaths(self):
        mtresult = mt.analyze(TEST_FILES_3)
        jsonpaths = mtresult.gen_redshift_jsonpaths()
        expected = {
            'jsonpaths': [
                "$['foo']['bar']",
                "$['qux']",
                "$['baz']['qux']"
        ]}
        self.assertListEqual(sorted(jsonpaths['jsonpaths']),
                             sorted(expected['jsonpaths']))

    def test_get_column_names(self):
        mtresult = mt.analyze(TEST_FILES_3)
        # Test hack
        mtresult.stats = {
            'foo.quz bar': {},
            'foo.bazBoo': {},
            'bar.FooBaz': {},
            'baz.foo-bar': {},
            'qux.BazBoo.foo baz.Foo-bar': {}
        }
        names = mtresult.get_cleaned_column_names()
        expected = [
            'baz_fooBar',
            'foo_quzBar',
            'bar_fooBaz',
            'foo_bazBoo',
            'qux_bazBoo_fooBaz_fooBar'
        ]
        self.assertListEqual(sorted(expected), sorted(names))
