#!/usr/bin/python


""" XML parsers.
"""


import os
from glob import glob

from lxml import etree

from memorize.log import Logger


log = Logger('memorize.parsers')


class ParsersManager(object):
    """ :py:class:`ParsersManager` collects all XML data files and uses
    parsers to create or update information holders.
    """

    def __init__(self, config):

        self.config = config
        self.parsers = config.xml_parsers

    def parse_file(self, file):
        """ Parses given XML file.
        """

        log.info(u'Parsing file: "{0}".', file)
        tree = etree.parse(file, etree.XMLParser(remove_blank_text=True))
        self.parse_node(tree.getroot())

    def parse_node(self, node):
        """ Parses XML node.
        """

        log.debug(u'Parsing node: {0}.', node.tag)

        try:
            parser = self.parsers[node.tag]
        except KeyError:
            raise ValueError(u'No parser for {0}.'.format(node.tag))
        parser.parse(self, node)

    def collect(self):
        """ Collects all ``*.mem`` files.
        """

        log.debug(u'Collecting data files.')

        files = []
        for directory in self.config.get_data_directories():
            path = os.path.join(directory, u'*.mem')
            log.debug(u'Searching files: \"{0}\".', path)
            for file in glob(path):
                files.append(file)
        return files


class ContainerNodeParser(object):
    """ :py:class:`ContainerNodeParser` parses XML ``container`` node.

    Parsing rules:

    +   nodes attributes ``tag`` value (or empty unicode string) is
        appended to all children nodes ``tag`` attributes (if they
        do not exist -- they are created);
    +   if node has attribute and child don't, then it creates that
        attribute to child attribute;
    +   calls parser for each children.

    """

    def parse(self, manager, node):
        """ Parses given ``container`` node.
        """

        attributes = node.attrib
        try:
            tags = attributes[u'tags']
            del attributes[u'tags']
        except KeyError:
            tags = u''
        for child in node:
            keys = set(child.keys())
            for key, value in attributes.items():
                if not key in keys:
                    child.set(key, value)
            child.set(
                    u'tags',
                    u'{0} {1}'.format(child.get(u'tags', u''), tags))
            manager.parse_node(child)
