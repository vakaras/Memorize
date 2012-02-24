#!/usr/bin/python


""" XML parsers.
"""


import os

from lxml import etree

from memorize.log import Logger
from memorize.tag_tree import Tag
from memorize import utils


log = Logger('memorize.parsers')


class ParsersManager(object):
    """ :py:class:`ParsersManager` collects all XML data files and uses
    parsers to create or update information holders.
    """

    def __init__(self, config):

        self.config = config
        self._tag_tree = config.tag_tree
        self.object_id_set = set()
        self.parsers = []
        self.parsers = config.get_xml_parsers(self)

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
        parser.parse(node)

    def collect(self):
        """ Collects all ``*.mem`` files.
        """

        log.debug(u'Collecting data files.')

        tag_files = []
        data_files = []
        for directory in self.config.get_data_directories():
            log.debug(u'Searching files: \"{0}\".', directory)
            for file in utils.find_files(directory, u'*.mem'):
                if file.endswith(u'tags.mem'):
                    tag_files.append(file)
                else:
                    data_files.append(file)
        return tag_files + data_files

    def mark_object_id(self, object_id):
        """ If object id is not used marks it as used. Otherwise raises
        error.

        :type object_id: int
        """

        if object_id in self.object_id_set:
            raise IntegrityError(
                    u'Object id {0} is already used.'.format(object_id))
        else:
            self.object_id_set.add(object_id)

    def get_tag_tree(self):
        """ Returns tag_tree.
        """

        return self._tag_tree

    def finalize(self):
        """ Call parsers to finalize their work.

        This function is called after all data files are parsed.
        """

        for parser in self.parsers.values():
            parser.finalize()


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

    def __init__(self, manager, persistent_data):
        """ This parser doesn't need to store data.
        """
        self.manager = manager

    def parse(self, node):
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
            self.manager.parse_node(child)

    def finalize(self):
        """ Because this parser haven't created any information holders
        there are nothing to finalize.
        """


class TagNodeParser(object):
    """ :py:class:`TagNodeParser` parses XML ``tag`` node.

    Creates tag with name, which is mentioned in attribute ``name``.

    """

    def __init__(self, manager, persistent_data):
        """ This parser doesn't need to store data.
        """

        self.manager = manager

    def parse(self, node):
        """ Parses given ``tag`` node.
        """

        tag = Tag(unicode(node.get(u'name')))
        tree = self.manager.get_tag_tree()
        tree.create_tag(tag)
        log.debug(u'Tag \"{0}\" in TagTree created.', unicode(tag))

    def finalize(self):
        """ Because this parser haven't created any information holders
        there are nothing to finalize.
        """
