__author__ = 'trollinger'

import unittest
import util
import shutil
import file_sys_manip
from backup import *


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.test_dir_path = file_sys_manip.generate_unique_path("test_dir")
        os.mkdir(self.test_dir_path)
        self.file_creator = file_sys_manip.FileCreator()

    def tearDown(self):
        shutil.rmtree(self.test_dir_path)

    def test_command_line_backup(self):
        # No arguments
        self.assertRaises(
            ArgumentException,
            lambda: command_line_backup(['file_name'])
        )
        # No input path
        self.assertRaises(
            ArgumentException,
            lambda: command_line_backup(['file_name', '-o', 'output_file'])
        )
        # Normal usage
        output_dir_path = os.path.dirname(self.test_dir_path)
        output_file_path = command_line_backup(['file_name', '-i', self.test_dir_path, '-o', output_dir_path])
        self.assertTrue(os.path.isfile(output_file_path))
        os.remove(output_file_path)

    def test_backup(self):
        output_dir_path = self.test_dir_path
        # input_path doesn't exist
        self.assertRaises(
            IOError,
            lambda: backup('does_not_exist', output_dir_path)
        )
        # output_dir_path doesn't exist
        self.assertRaises(
            IOError,
            lambda: backup(self.test_dir_path, 'does_not_exist')
        )
        # Check specified output dir
        backup_file_path = backup(self.test_dir_path, output_dir_path)
        self.assertTrue(os.path.exists(backup_file_path))
        os.remove(backup_file_path)
