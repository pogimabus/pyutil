import unittest
import os
import shutil
import re
import file_sys_manip


def is_text_in_file(text, file_path):
    """
    Returns true if the given text is found in the file at the given path, false otherwise
    @type text: str
    @param text: text to search for
    @type file_path: str
    @param file_path: path of the file that will be searched
    @rtype bool
    @return: true if the given text is found in the file at the given path, false otherwise
    """
    with open(file_path, 'r') as f:
        for line in f:
            if text in line:
                return True
    return False


def is_pattern_in_file(pattern, file_path):
    """
    Returns true if the given pattern is found in the file at the given path, false otherwise
    @type pattern: str
    @param pattern: str which will be interpreted as a regular expression and then searched for
    @type file_path: str
    @param file_path: path of the file that will be searched
    @rtype bool
    @return: true if the given pattern is found in the file at the given path, false otherwise
    """
    pattern = re.compile(pattern)
    with open(file_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match is not None:
                return True
    return False


class FileSearchTests(unittest.TestCase):

    def setUp(self):
        self.test_dir = file_sys_manip.generate_unique_path("test_dir")
        os.mkdir(self.test_dir)
        self.file_creator = file_sys_manip.FileCreator()
        self.file_path = self.file_creator.create_unique_file(dir_path=self.test_dir)
        with open(self.file_path, 'w') as f:
            f.write("[These] are not the droids you're looking for.")

    def tearDown(self):
        self.file_creator.delete_all_created_files()
        shutil.rmtree(self.test_dir)

    def test_is_text_in_file(self):
        self.assertFalse(is_text_in_file("not in file", self.file_path))
        self.assertTrue(is_text_in_file("roids y", self.file_path))

    def test_is_pattern_in_file(self):
        self.assertTrue(is_pattern_in_file("{}.*for.$".format(re.escape("hese]")), self.file_path))
        self.assertFalse(is_pattern_in_file("^a", self.file_path))
