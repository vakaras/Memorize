#!/usr/bin/python


""" Utils module.
"""


import os
import fnmatch
from termcolor import colored


class Writer(object):
    """ Class which purpose is to help to print nice messages to terminal.
    """

    def __init__(self, file=None):
        if file is None:
            import sys
            self.file = sys.stdout
            del sys
        else:
            self.file = file

    def write(self, template, *args, **kwargs):
        """ Writes ``template`` formated with info provided in ``args``
        and ``kwargs`` to file.

        If arg is 2 element tuple, then it is assumed that second
        argument is color name to be used.

        :param template: String to be formated.
        :type template: unicode
        """

        arguments = []
        for i, arg in enumerate(list(args)):
            if isinstance(arg, tuple) and len(arg) == 2:
                arguments.append(colored(*arg))
            else:
                arguments.append(arg)

        for key, arg in list(kwargs.items()):
            if isinstance(arg, tuple) and len(arg) == 2:
                kwargs[key] = colored(*arg)

        self.file.write(template.format(*arguments, **kwargs))

    def write_string(self, string, color=None):
        """ Writes string to file in given color.
        """

        if color:
            self.file.write(colored(string, color))
        else:
            self.file.write(string)


def find_files(directory, pattern):
    """ Searches recursively for files matching pattern in directory.
    """

    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                yield os.path.join(root, basename)
