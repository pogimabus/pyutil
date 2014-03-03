import sys
import unittest


class DummyFile(object):
    def write(self, x):
        pass


class NoStdout():
    def __enter__(self):
        self.save_stdout = sys.stdout
        sys.stdout = DummyFile()

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.save_stdout


def create_visual_studio_error(file_path='', line_number=1, msg='', warning=False):
    severity = "warning" if warning else "error"
    return "{}({}) : {} : {}\n".format(file_path, line_number, severity, msg)


def insert_at_index(val, index, slicable):
    return slicable[0:index] + val + slicable[index:]


class UtilTests(unittest.TestCase):
    def test_insert_at_index(self):
        string = "test"
        self.assertTrue(insert_at_index('2', 2, string) == 'te2st')
