#!/usr/bin/python


""" XML parsers.
"""


import os
from glob import glob

from lxml import etree

from memorize.log import Logger
from memorize.tag_tree import Tag


log = Logger('memorize.parsers')


class ParsersManager(object):
    """ :py:class:`ParsersManager` collects all XML data files and uses
    parsers to create or update information holders.
    """

    def __init__(self, config):

        self.config = config
        self.parsers = config.xml_parsers
        self._tag_tree = config.tag_tree
        self.object_id_set = set()

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

    def __init__(self, persistent_data):
        """ This parser doesn't need to store data.
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

    def finalize(self):
        """ Because this parser haven't created any information holders
        there are nothing to finalize.
        """


class TagNodeParser(object):
    """ :py:class:`TagNodeParser` parses XML ``tag`` node.

    Creates tag with name, which is mentioned in attribute ``name``.

    """

    def __init__(self, persistent_data):
        """ This parser doesn't need to store data.
        """

    def parse(self, manager, node):
        """ Parses given ``tag`` node.
        """

        tag = Tag(node.get(u'name').decode('utf-8'))
        tree = manager.get_tag_tree()
        tree.create_tag(tag)
        log.debug('Tag \"{0}\" in TagTree created.', unicode(tag))

    def finalize(self):
        """ Because this parser haven't created any information holders
        there are nothing to finalize.
        """
