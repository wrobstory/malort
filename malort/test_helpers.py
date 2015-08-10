# -*- coding: utf-8 -*-
"""
Malort Test Helpers

Test Runner: PyTest

"""
import os
import unittest


TEST_FILES_1 = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                '..', 'tests', 'test_files'))
TEST_FILES_2 = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                '..', 'tests', 'test_files_newline_delimited'))
TEST_FILES_3 = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                '..', 'tests', 'test_files_nested'))
TEST_FILES_4 = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                '..', 'tests', 'test_files_mult_type'))

class TestHelpers(unittest.TestCase):

    def assert_stats(self, result, expected):
        """Test helper for testing stats results"""
        for key, value in result.items():
            for typek, typev in value.items():
                if typek == 'str':
                    for k, v in typev.items():
                        if isinstance(v, list):
                            self.assertTrue(len(v) <= 3)
                            for item in v:
                                self.assertIn(item, expected[key][typek][k])
                        else:
                            self.assertEquals(expected[key][typek][k], v)
                elif typek == 'base_key':
                    self.assertEquals(typev, expected[key][typek])
                else:
                    self.assertDictEqual(typev, expected[key][typek])