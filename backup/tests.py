__author__ = 'trollinger'

import unittest
from backup import *


class BackupTests(unittest.TestCase):
    def test_main(self):
        # No arguments
        self.assertRaises(
            ArgumentException,
            lambda _: main(['file_name'])
        )

        # No input path
        self.assertRaises(
            ArgumentException,
            lambda _: main(['file_name', '-o', 'output_file'])
        )

        # Normal Usage
        self.assertTrue()
