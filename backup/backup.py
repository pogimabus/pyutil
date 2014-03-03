"""
This utility creates a time stamped zip backup of the file/directory
specified by '-i' to the directory specified by'-o'
"""
__author__ = 'Dwight Trollinger'


import sys
import zipfile
import os
import datetime
import file_sys_manip


def main(args):
    try:
        command_line_backup(args)
    except ArgumentException as e:
        print e.message
        exit(1)


def command_line_backup(args):
    if len(args) == 1:
        raise ArgumentException(__doc__)
    input_path = None
    output_dir_path = None
    for index, arg in enumerate(args):
        if arg == '-i' or arg == '-o':
            if index + 1 == len(args):
                raise ArgumentException("Missing input directory path after '{}'".format(arg))
            elif arg == '-i':
                input_path = args[index+1]
            elif arg == '-o':
                output_dir_path = args[index+1]
    if input_path is None:
        raise ArgumentException("You must specify directory/file to back up (-i)")
    print "Backing up {} to {}...".format(input_path, output_dir_path)
    output_file_path = backup(input_path, output_dir_path)
    print "Complete."
    return output_file_path


def backup(input_path, output_dir_path=None):
    """
    Creates a timestamped zipped copy of the file/directory with the given input_path in the directory with the given
        output_dir_path

    @type input_path: str
    @param input_path: the path of the file/directory to back up
    @type output_dir_path: str
    @param output_dir_path: the path of the directory to place to backup in
    """
    if not os.path.exists(input_path):
        raise IOError("{} does not exist.".format(input_path))
    # Default output to the parent directory of input
    if output_dir_path is None:
        output_dir_path = os.path.dirname(input_path)

    # Get the time stamp
    now = datetime.datetime.now()
    time_stamp = [now.year, now.month, now.day, now.hour, now.minute, now.second]
    time_stamp = [str(entry) for entry in time_stamp]
    time_stamp = '_'.join(time_stamp)
    output_file_name = os.path.basename(input_path) + '_' + time_stamp
    output_file_path = os.path.join(output_dir_path, output_file_name) + '.zip'
    if os.path.isdir(input_path):
        file_sys_manip.zip_dir(input_path, output_file_path)
    elif os.path.isfile(input_path):
        with zipfile.ZipFile(output_file_path, 'w+', zipfile.ZIP_DEFLATED) as z:
            z.write(input_path)
    else:
        raise ArgumentException("{} does not exist".format(input_path))
    return output_file_path


class ArgumentException(Exception):
    pass


if __name__ == '__main__':
    main(sys.argv)
