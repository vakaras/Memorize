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

from BTrees.OOBTree import OOBTree

from memorize import db
from memorize.tag_tree import TagTree
from memorize.holders import InformationHolderPlugin
from memorize.parsers import ContainerNodeParser, TagNodeParser
from memorize.manipulators import ManipulatorPlugin


DEFAULT_CONFIGURATION = {

    # Location of ZODB file.
    'database_path': os.path.join(
        os.getenv(u'HOME'), u'.memorize', u'db', u'data.fs'),
    # Connect to ZODB at program start or wait until it is asked.
    'connect_to_db': False,
    # Automatically create needed directories.
    'create_directories': True,

    'plugins': [
        # Holders.
        'memorize.holders.word.WordPlugin',

        # Manipulators.
        'memorize.manipulators.word.WordManipulatorPlugin',
        ],

    # Directories to be searched for *.mem files.
    'data_directories': [
        os.path.join(os.getenv(u'HOME'), u'.memorize', u'data'),
        ],
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

        self._plugins = None
        self._xml_parsers = None
        self._manipulators = None

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

    @property
    def tag_tree(self):
        """ Returns Tag Tree object.
        """

        root = self.db_root
        if not root.has_key(u'tree'):
            root['tree'] = TagTree()
        return root['tree']

    def collect_xml_parsers(self):
        """ Collects XML parsers from registered plugins.
        """

        self.load_plugins()

        parsers_data = db.create_or_get(
                self.db_root, 'parsers_data', OOBTree)

        self._xml_parsers = {
                u'container': ContainerNodeParser(
                    db.create_or_get(parsers_data, 'container', OOBTree)),
                u'tag': TagNodeParser(
                    db.create_or_get(parsers_data, 'tag', OOBTree)),
                }
        for plugin in InformationHolderPlugin.plugins:
            self._xml_parsers[plugin.tag_name] = plugin.xml_parser(
                    db.create_or_get(parsers_data, plugin.tag_name, OOBTree)
                    )

    def collect_manipulators(self):
        """ Collects manipulators from registered plugins.
        """

        self.load_plugins()
        self._manipulators = ManipulatorPlugin.plugins[:]

    def load_plugins(self):
        """ Loads plugins.
        """

        if self._plugins is not None:
            # Plugins already loaded.
            return

        self._plugins = []

        for plugin_path in self._data['plugins']:
            parts = plugin_path.split('.')
            try:
                module = __import__(
                        '.'.join(parts[:-1]), fromlist=parts[-1])
            except ImportError:
                raise ConfigurationError(
                        u'Failed to load plugin: {0}.'.format(
                            plugin_path.decode('utf-8')))
            self._plugins.append(module)

    @property
    def xml_parsers(self):
        """ Returns list of XML parsers.
        """

        if self._xml_parsers is None:
            self.collect_xml_parsers()

        return self._xml_parsers

    @property
    def manipulators(self):
        """ Returns list of manipulators.
        """

        if self._manipulators is None:
            self.collect_manipulators()

        return self._manipulators

    def get_data_directories(self):
        """ Returns paths to directories, which should be searched for
        ``*.mem`` files.
        """

        return self._data['data_directories']
