# -*- coding: utf-8 -*-
"""
Malort Tests

Test Runner: PyTest

"""
import os
import unittest

import malort as mt


TEST_FILES_1 = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                '..', 'test_files'))
TEST_FILES_2 = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                '..', 'test_files_delimited'))


class TestDictGenerator(unittest.TestCase):

    def test_json_files_newline(self):
        gen = mt.core.dict_generator(TEST_FILES_1)
        self.assertEquals(len([d for d in gen]), 4)

    def test_json_files_pipe(self):
        gen = mt.core.dict_generator(TEST_FILES_2, '|')
        self.assertEquals(len([d for d in gen]), 4)


class TestUpdateEntryStats(unittest.TestCase):

    def test_stats_str(self):
        update_1 = mt.core.update_entry_stats('Foooo', {})
        self.assertEquals(update_1,
                         {'count': 1, 'mean': 5.0, 'max': 5,
                          'min': 5})

        update_2 = mt.core.update_entry_stats('Foooo', {'str': update_1})
        self.assertEquals(update_2,
                          {'count': 2, 'mean': 5.0, 'max': 5,
                           'min': 5})

        update_3 = mt.core.update_entry_stats('Foo', {'str': update_2})
        self.assertEquals(update_3,
                          {'count': 3, 'mean': 4.333, 'max': 5,
                           'min': 3})

    def test_stats_bool(self):
        update_1 = mt.core.update_entry_stats(True, {})
        self.assertEquals(update_1, {'count': 1})

        update_2 = mt.core.update_entry_stats(False, {'bool': update_1})
        self.assertEquals(update_2, {'count': 2})

    def test_stats_number(self):
        update_1 = mt.core.update_entry_stats(1, {})
        self.assertEquals(update_1,
                          {'count': 1, 'mean': 1.0, 'max': 1,
                           'min': 1})

        update_2 = mt.core.update_entry_stats(2.0, {'int': update_1})
        self.assertEquals(update_2,
                          {'count': 1, 'mean': 2.0, 'max': 2.0,
                           'min': 2.0})

        update_3 = mt.core.update_entry_stats(2, {'int': update_1,
                                                  'float': update_2})
        self.assertEquals(update_3,
                          {'count': 2, 'mean': 1.5, 'max': 2,
                           'min': 1})

        update_4 = mt.core.update_entry_stats(4.0, {'int': update_3,
                                                    'float': update_2})
        self.assertEquals(update_4,
                          {'count': 2, 'mean': 3.0, 'max': 4.0,
                           'min': 2.0})