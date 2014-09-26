# -*- coding: utf-8 -*-
"""
Malort Mapper Tests

Test Runner: PyTest

"""
import unittest

import malort as mt
from malort.test_helpers import (TestHelpers, TEST_FILES_1, TEST_FILES_2,
                                 TEST_FILES_3)


class TestTypeMappers(unittest.TestCase):

    def test_files_1(self):
        mtresult = mt.analyze(TEST_FILES_1)
        types = mtresult.get_redshift_types()
        expected = {
            'varcharfield': 'varchar(12)',
            'charfield': 'char(11)',
            'intfield': 'SMALLINT',
            'floatfield': 'REAL'
        }
        self.assertDictEqual(types, expected)

    def test_files_2(self):
        mtresult = mt.analyze(TEST_FILES_2, '|')
        types = mtresult.get_redshift_types()
        for k, v in types.items():
            self.assertEqual(v, 'Multiple types detected.')

    def test_files_3(self):
        mtresult = mt.analyze(TEST_FILES_3)
        types = mtresult.get_redshift_types()
        expected = {
            'baz.qux': 'varchar(5)',
            'foo.bar': 'SMALLINT',
            'qux': 'BOOLEAN'
        }
        self.assertDictEqual(types, expected)


class TestRedshiftMapper(unittest.TestCase):

    rs = mt.type_mappers.RedshiftMapper

    def test_booleans(self):
        self.assertEqual(self.rs.booleans({}), "BOOLEAN")

    def test_strings(self):
        stats = {'min': 5, 'max': 5, 'mean': 5.0, 'sample': ['Foo']}
        self.assertEqual(self.rs.strings(stats), 'char(5)')

        stats['max'] = 70000
        self.assertEqual(self.rs.strings(stats),
                         'Too large for any char column!')

        stats['max'] = 6
        self.assertEqual(self.rs.strings(stats), 'varchar(6)')

        stats['sample'] = ['TRUE', 'FALSE', 'TRUE']
        self.assertEqual(self.rs.strings(stats), "BOOLEAN")

        stats['sample'] = ['t', 'yes', 'false']
        self.assertEqual(self.rs.strings(stats), "BOOLEAN")

    def test_ints(self):
        stats = {'min': 45, 'max': 45}
        self.assertEqual(self.rs.ints(stats), 'SMALLINT')

        stats['min'], stats['max'] = -40000, 4000
        self.assertEqual(self.rs.ints(stats), 'INTEGER')

        stats['min'] = -3000000000
        stats['max'] = 3000000000
        self.assertEqual(self.rs.ints(stats), 'BIGINT')

    def test_floats(self):
        stats = {'fixed_length': True, 'max_precision': 6, 'max_scale': 5}
        self.assertEqual(self.rs.floats(stats), 'decimal(6, 5)')

        stats['max_scale'] = 39
        self.assertEqual(self.rs.floats(stats), 'REAL')

        stats['max_precision'] = 7
        self.assertEqual(self.rs.floats(stats), 'FLOAT')