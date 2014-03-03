import unittest
import os
import shutil
import time
import re
import zipfile


file_line_list_cache = {}
file_line_list_cache_lowered = {}


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def get_file_line_list_from_cache(file_path, lowered=False):
    if lowered:
        if file_path not in file_line_list_cache_lowered:
            with open(file_path, 'r') as f:
                line_list = [line.lower() for line in f]
            file_line_list_cache_lowered[file_path] = line_list
        line_list = file_line_list_cache_lowered[file_path]
    else:
        if file_path not in file_line_list_cache:
            with open(file_path, 'r') as f:
                line_list = [line for line in f]
            file_line_list_cache[file_path] = line_list
        line_list = file_line_list_cache[file_path]
    return line_list


def generate_unique_path(base_path, parent_dir=None):
    if parent_dir is None:
        parent_dir = os.getcwd()
    base_path = os.path.join(parent_dir, base_path)
    if not os.path.exists(base_path):
        unique_path = base_path
    else:
        count = 0
        base_path_name, base_path_extension = os.path.splitext(base_path)
        while True:
            count += 1
            unique_path = "{}_{}{}".format(base_path_name, count, base_path_extension)
            if not os.path.exists(unique_path):
                break
    # noinspection PyUnboundLocalVariable
    return os.path.abspath(unique_path)


def get_file_paths(dir_paths, extensions=None, excluded_dir_paths=None):
    """
    Returns the set of every file path in the specified directory trees which has one of the given extensions
    @type dir_paths: str or set
    @param dir_paths: set of directory paths to search
    @type extensions: set
    @param extensions: set of extensions file paths will be checked against
    @type excluded_dir_paths: unknown or str or dict or set
    @param excluded_dir_paths: set of directory paths to exclude from the search
    @return: the set of every file path in the specified directory trees
    """
    if isinstance(dir_paths, str):
        dir_paths = {dir_paths}
    if isinstance(excluded_dir_paths, str):
        excluded_dir_paths = {excluded_dir_paths}
    if excluded_dir_paths is None:
        excluded_dir_paths = set()
    paths = set()
    for dir_path in dir_paths:
        for root_path, dir_names, file_names in os.walk(dir_path):
            if root_path not in excluded_dir_paths:
                for file_name in file_names:
                    if extensions is None or os.path.splitext(file_name)[1][1:] in extensions:
                        paths.add(os.path.join(root_path, file_name))
    return paths


class FileCreator(object):

    def __init__(self):
        self.files_created = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete_all_created_files()

    def create_unique_file(self, base_name=None, dir_path=None):
        """
        Creates a uniquely named file in the given directory path
        @type base_name: str
        @param base_name: the base name of the file we want to create
        @type dir_path: str
        @param dir_path: the path to the directory where the file shall be created
        @rtype str
        @return: the path of the newly created file
        """
        if dir_path is None:
            dir_path = os.getcwd()
        if base_name is None:
            base_name = "test_file.txt"
        file_path = generate_unique_path(os.path.join(dir_path, base_name))
        self.touch(file_path)
        return file_path

    def touch(self, file_path):
        touch(file_path)
        self.files_created.append(file_path)

    def create_files_from_dict(self, file_dict, dir_path=None):
        """
        Creates files based on a file_dict.
        @type file_dict: dict
        @param file_dict: dict of the form { file_path_str: file_contents_str }
        @param dir_path: Directory path which relative file_path_str will be based upon
        @return: None
        """
        if dir_path is None:
            dir_path = os.getcwd()
        for file_path, contents in file_dict.iteritems():
            full_path = os.path.join(dir_path, file_path)
            if os.path.exists(full_path):
                raise FileAlreadyExists("File '{}' already exists and therefor not be created as specified".format(
                    file_path))
            with open(full_path, 'w+') as f:
                f.write(contents)
            self.files_created.append(full_path)

    def delete_all_created_files(self):
        remove_files(self.files_created)
        self.files_created = []


def remove_files(file_paths, parent_dir=None):
    """
    Deletes the files specified by file_paths
    @param file_paths: paths of the files that will be deleted
    @return: None
    """
    if parent_dir is None:
        parent_dir = os.getcwd()
    for file_path in file_paths:
        try:
            os.remove(os.path.join(parent_dir, file_path))
        except WindowsError:
            pass


def zip_dir(input_dir_path, output_file_path):
    if not os.path.isdir(input_dir_path):
        raise DirectoryError("{} is not a directory")
    with zipfile.ZipFile(output_file_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(input_dir_path):
            for f in files:
                z.write(os.path.join(root, f))


class DirectoryError(Exception):
    pass


class FileAlreadyExists(Exception):
    pass


#--------------------
# Tests
#--------------------
class FileCreatorTests(unittest.TestCase):

    def setUp(self):
        self.test_dir = generate_unique_path("test_dir")
        os.mkdir(self.test_dir)
        self.file_creator = FileCreator()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_touch(self):
        with FileCreator() as file_creator:
            file_path = generate_unique_path(self.test_dir)
            file_creator.touch(file_path)
            self.assertTrue(os.path.exists(file_path))

    def test_with(self):
        with FileCreator() as file_creator:
            file_path = generate_unique_path(self.test_dir)
            file_creator.touch(file_path)
        self.assertFalse(os.path.exists(file_path))

    def test_create_test_file(self):
        file_name = "create_test_file_test_file.txt"
        file_path = self.file_creator.create_unique_file(file_name, self.test_dir)
        self.assertTrue(os.path.abspath(self.test_dir) == os.path.abspath(os.path.dirname(file_path)))
        self.assertTrue(os.path.basename(file_path) == file_name)
        self.assertTrue(os.path.exists(file_path))
        self.file_creator.delete_all_created_files()

    def test_create_files_from_dict(self):
        file_dict = {"test_file_from_dict": "contents", "test_file_from_dict_2": "contents2"}
        self.file_creator.create_files_from_dict(file_dict, self.test_dir)
        for file_path, contents in file_dict.iteritems():
            with open(os.path.join(self.test_dir, file_path), 'r') as f:
                self.assertTrue(f.read() == contents)
        self.file_creator.delete_all_created_files()

    def test_delete_all_created_files(self):
        test_file_base_name = "test_delete_all_files_created.txt"

        # Basic test
        files_created = set()

        files_created.add(self.file_creator.create_unique_file(self.test_dir))

        dict_file_path = generate_unique_path(test_file_base_name)
        self.file_creator.create_files_from_dict({dict_file_path: ""})
        files_created.add(dict_file_path)

        self.file_creator.delete_all_created_files()
        for file_path in files_created:
            self.assertFalse(os.path.exists(file_path))

        # Test that it works twice in a row
        files_created = set()

        dict_file_path = generate_unique_path(test_file_base_name)
        self.file_creator.create_files_from_dict({dict_file_path: ""})
        files_created.add(dict_file_path)

        files_created.add(self.file_creator.create_unique_file(self.test_dir))

        self.file_creator.delete_all_created_files()
        for file_path in files_created:
            self.assertFalse(os.path.exists(file_path))


class FileSysManipTests(unittest.TestCase):

    def setUp(self):
        self.test_dir = generate_unique_path("test_dir")
        os.mkdir(self.test_dir)
        self.file_creator = FileCreator()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_file_line_list_from_cache(self):
        base_test_file_name = "test_get_file_line_list_from_cache.txt"
        test_file_list = ["hurble\n", "durble"]
        test_files = {
            generate_unique_path(base_test_file_name): "".join(test_file_list)
        }
        self.file_creator.create_files_from_dict(test_files, self.test_dir)
        for f in test_files:
            self.assertTrue(test_file_list == get_file_line_list_from_cache(f))
        self.file_creator.delete_all_created_files()

    def test_touch_create(self):
        touch_path = self.file_creator.create_unique_file(dir_path=self.test_dir)
        self.assertTrue(os.path.exists(touch_path))
        self.file_creator.delete_all_created_files()

    def test_touch_update_time(self):
        touch_path = self.file_creator.create_unique_file(dir_path=self.test_dir)
        touch_time = os.path.getmtime(touch_path)
        time.sleep(0.1)
        touch(touch_path)
        self.assertTrue(touch_time != os.path.getmtime(touch_path))
        self.file_creator.delete_all_created_files()

    def test_generate_unique_path(self):
        base_path = os.path.join(self.test_dir, "path_gen_test_file.txt")
        base_path_name, base_path_extension = os.path.splitext(base_path)
        paths = set()
        for i in xrange(100):
            new_path = generate_unique_path(base_path)

            # Check the formatting of the new path
            pattern = re.compile("^{}_?[0-9]*{}".format(re.escape(base_path_name), re.escape(base_path_extension)))
            self.assertTrue(pattern.match(new_path) is not None)
            # Make sure the path is unique
            self.assertTrue(new_path not in paths)
            self.assertFalse(os.path.exists(new_path))

            touch(new_path)
            paths.add(new_path)
        # Cleanup
        for p in paths:
            os.remove(p)

    def test_remove_files(self):
        base_file_name = "test_remove_files.txt"
        # Test multiple files
        file_paths = []
        for i in xrange(20):
            file_paths.append(generate_unique_path(base_file_name, self.test_dir))
            touch(file_paths[-1])
        remove_files(file_paths)
        for file_path in file_paths:
            self.assertFalse(os.path.exists(file_path))
        # Test parent_dir
        file_path = generate_unique_path(base_file_name, self.test_dir)
        touch(file_path)
        remove_files([os.path.basename(file_path)], self.test_dir)

    def test_get_file_paths(self):
        deep_path = os.path.join(self.test_dir, "deep\\path")
        os.makedirs(deep_path)
        with FileCreator() as file_creator:
            extensions = {"ext", "ext2"}
            # Test normal usage
            test_files = {
                os.path.join(deep_path, "get_file_path_1.ext"): "",
                "get_file_path_2.ext2": "",
                "get_file_path_3.not_in_extns": "",
            }
            file_creator.create_files_from_dict(test_files, self.test_dir)
            found = get_file_paths(self.test_dir, extensions)
            expected = {
                os.path.join(self.test_dir, 'get_file_path_2.ext2'),
                os.path.join(self.test_dir, 'deep\\path\\get_file_path_1.ext'),
            }
            self.assertTrue(found == expected)

            # Test directory exclusion
            found = get_file_paths(self.test_dir, extensions, deep_path)
            expected = {os.path.join(self.test_dir, 'get_file_path_2.ext2')}
            self.assertTrue(found == expected)

    def test_zip_dir(self):
        top_dir_path = os.path.join(self.test_dir, 'test_zip_dir')
        zip_file_path = top_dir_path + '.zip'
        deep_path = os.path.join(top_dir_path, r'zip\dir')
        os.makedirs(deep_path)
        files = {
            os.path.join(deep_path, 'zip_file'): 'This is a file that will be zipped.',
            'top_zip_file': 'This is a file that will be zipped.'
        }
        self.file_creator.create_files_from_dict(
            files,
            top_dir_path)
        zip_dir(top_dir_path, zip_file_path)
        with zipfile.ZipFile(zip_file_path, 'r') as zfile:
            zipped_file_names = set([os.path.basename(file_path) for file_path in zfile.namelist()])
        self.assertTrue(set([os.path.basename(file_path) for file_path in files]) == zipped_file_names)
