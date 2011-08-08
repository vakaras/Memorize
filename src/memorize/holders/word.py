#!/usr/bin/python


""" Information holder for words.
"""


import warnings

import persistent
from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree

from memorize.log import Logger
from memorize import db
from memorize.memorizable import Memorizable
from memorize.holders import InformationHolderPlugin
from memorize.tag_tree import TaggedObject, TagList


log = Logger('memorize.holders.word')


class Meaning(persistent.Persistent):
    """ Class representing one meaninig of word.
    """

    def __init__(self, value):

        self.value = value
        self.words = IOBTree()

    def add_word(self, word):
        """ Appends word to words, which have the same meaning, list.
        """

        self.words[word.get_id()] = word

    def get_word_list(self):
        """ Returns list of words, which have this meaning.
        """

        return self.words.values()


class WordMeaning(Memorizable):
    """ The memorizable meaning of concrete word.
    """

    def __init__(self, meaning, comment):
        """
        :type meaning: :py:class:`Meaning`
        :type comment: unicode
        """

        super(WordMeaning, self).__init__()

        self.meaning = meaning
        self.comment = comment

    def get_date_key(self):
        """ Returns key for use in ``meanings_date`` dictionary.
        """

        return u' -*- '.join([
            self.get_next_practice_unicode(),
            self.meaning.value])


class Word(TaggedObject):
    """ Generic word.

    This class is designed to be base class for various words, but also it
    can be used without modification.
    """

    def __init__(self, value=None, parts=(), translations=()):
        """

        :param value: The word itself.
        :type value: unicode
        :param parts:
            Other words, from which this is composed. (For example,
            Kinderzimmer is composed from Kind and Zimmer.)
        :type parts: iterable of :py:class:`words <Word>`

        .. note::
            If ``value`` is not passed to constructor, that attribute is
            not created at all. (Because, for example, for class
            representing German verb attribute ``value`` can be
            meaningless.)

        """

        super(Word, self).__init__()

        if value is not None:
            self.value = value

        self.part_of = IOBTree()
        self.parts = list(parts)
        self.meanings = list(translations)

    def create_links(self, words, meanings):
        """
        This function is called, when all data is read from files, to
        create links between words.

        .. todo::
            Implement Word comments and WordMeaning comments.
        """

        if isinstance(self.parts, list):
            # Creating new.
            parts = self.parts
            self.parts = IOBTree()
            for value in parts:
                for word in words[value]:
                    log.debug(
                            u'{0} ({1}) is part of {2} ({3}).',
                            word.value, word.get_id(),
                            self.value, self.get_id())
                    self.parts[word.get_id()] = word
                    word.add_composed(self)
        else:
            # Updating.
            warnings.warn(u'Word updating is not implemented. Skipping.')

        if isinstance(self.meanings, list):
            # Creating new.
            translations = self.meanings
            self.meanings = OOBTree()
            self.meanings_date = OOBTree()
            for translation in translations:
                try:
                    meaning = meanings[translation]
                except KeyError:
                    meaning = Meaning(translation)
                    meanings[translation] = meaning

                word_meaning = WordMeaning(meaning, u'')
                                        # TODO: Add meaning comments.

                self.meanings[translation] = word_meaning
                self.meanings_date[word_meaning.get_date_key()
                        ] = word_meaning
                meaning.add_word(self)
                log.debug(
                        u'Word {0} ({1}) has meaning {2}',
                        self.value, self.get_id(),
                        word_meaning.meaning.value)
        else:
            # Updating.
            warnings.warn(u'Word updating is not implemented. Skipping.')


    def add_composed(self, word):
        """ Adds word, in which this word is part to list.
        """

        self.part_of[word.get_id()] = word


class XMLWordParser(object):
    """ Extracts information about Words.
    """

    def __init__(self, persistent_data):

        self.words = {}
        self.meanings = db.create_or_get(
                persistent_data, u'meanings', OOBTree)


    def parse(self, manager, node):
        """ Parses given ``word`` node.
        """

        object_id = int(node.get(u'id'))
        manager.mark_object_id(object_id)

        value = node.get(u'value', '').decode('utf-8').strip()
        if len(value) == 0:
            raise Exception(u'Word value cannot be empty.')

        tags = TagList(node.get(u'tags', ''))

        translations = []
        parts = []
        for child in node:
            if child.tag == u'translation':
                translations.append(child.text)
            elif child.tag == u'part':
                parts.append(child)

        tree = manager.get_tag_tree()

        try:
            word = tree.get_object(object_id)
            warnings.warn(u'Word updating is not implemented. Skipping.')
        except KeyError:
            word = Word(value, parts, translations)
            tree.assign(word, object_id)
            for tag in tags:
                word.add_tag(tag)

        try:
            self.words[value].append(word)
        except KeyError:
            self.words[value] = [word]

    def finalize(self):
        """ This function is called, when all data is parsed.
        """
        log.debug(u'Finalizing words: creating interlinks.')

        for words in self.words.values():
            for word in words:
                word.create_links(self.words, self.meanings)


class WordPlugin(InformationHolderPlugin):
    """ Registering plugin.
    """

    tag_name = u'word'
    xml_parser = XMLWordParser
