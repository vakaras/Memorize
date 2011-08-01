#!/usr/bin/python


""" Information holder for words.
"""


from memorize.holders import InformationHolderPlugin


class XMLWordParser(object):
    """ Extracts information about Words.
    """

    def parse(self, manager, node):
        """ Parses given ``word`` node.
        """

        for key, value in node.attrib.items():
            print key, value


class WordPlugin(InformationHolderPlugin):
    """ Registering plugin.
    """

    tag_name = u'word'
    xml_parser = XMLWordParser
