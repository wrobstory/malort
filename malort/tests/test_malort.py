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