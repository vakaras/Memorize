#!/usr/bin/python


""" Configuration manager for :py:module:`memorize`.

In config file Python dict with configuraion values should be defined.
An example:

>>> config = {
...     'database_path': u'/home/foo/memorize/db.fs',
...     }

"""


import os
import errno
import shutil

from memorize import db

DEFAULT_CONFIGURATION = {

    # Location of ZODB file.
    'database_path': os.path.join(
        os.getenv(u'HOME'), u'.memorize', u'db', u'data.fs'),
    # Connect to ZODB at program start or wait until it is asked.
    'connect_to_db': False,
    # Automatically create needed directories.
    'create_directories': False,

    }


class ConfigManager(object):
    """ Base configuration class with default values.
    """

    def __init__(self, config_dict):
        """
        :type config_dict: dict
        :param confi_dict: dictionary with configuration values.
        """

        self._data = DEFAULT_CONFIGURATION.copy()
        self._data.update(config_dict)

        self._db_root = None
        if self._data['connect_to_db']:
            self.connect()

    def connect(self):
        """ Connects to ZODB.
        """

        if self._data['create_directories']:
            path = os.path.dirname(self._data['database_path'])
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    pass
                else:
                    raise
            else:
                print 'Created directory: {0}.'.format(path)

        self._db_root = db.connect(self._data['database_path'])

    @property
    def db_root(self):
        """ Returns ZODB root dictionary.
        """

        if self._db_root is None:
            self.connect()
        return self._db_root
