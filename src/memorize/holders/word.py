#!/usr/bin/python


""" Information holder for words.
"""


import warnings
import functools

import persistent
from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree

from memorize.log import Logger
from memorize.utils import Writer
from memorize import db
from memorize.memorizable import Memorizable
from memorize.holders import InformationHolderPlugin
from memorize.tag_tree import TaggedObject, TagList, Tag


log = Logger('memorize.holders.word')


class Example(persistent.Persistent):
    """ Example of word use.
    """

    def __init__(self, number, original, translation):
        self.number = number
        self.original = original
        self.translation = translation


class Meaning(persistent.Persistent):
    """ Class representing one meaninig of word.

    .. todo::

        Add utility, which removes meanings, to which none words are
        linked.
    """

    def __init__(self, value):

        self.value = value
        self.words = IOBTree()

    def __unicode__(self):
        return u'Meaning: {0.value}'.format(self)

    def add_word(self, word):
        """ Appends word to words, which have the same meaning, list.
        """

        self.words[word.get_id()] = word

    def remove_word(self, word):
        """ Removes word from words, which have the same meaning, list.
        """

        del self.words[word.get_id()]

    def get_word_list(self):
        """ Returns list of words, which have this meaning.
        """

        return self.words.values()


class WordMeaning(Memorizable):
    """ The memorizable meaning of concrete word.
    """

    def __init__(self, word, meaning, comment, examples=()):
        """
        :type meaning: :py:class:`Meaning`
        :type meaning: :py:class:`Word`
        :type comment: unicode
        """

        super(WordMeaning, self).__init__()

        self.meaning = meaning
        self.word = word
        self.comment = comment
        self.examples = tuple(examples)

    def get_date_key(self):
        """ Returns key for use in ``meanings_date`` dictionary.
        """

        return u' -*- '.join([
            self.get_next_practice_unicode(),
            self.meaning.value,
            unicode(id(self))])


@functools.total_ordering
class Word(TaggedObject):
    """ Generic word.

    This class is designed to be base class for various words, but also it
    can be used without modification.
    """

    def __init__(self, value=None, comment=u'', parts=(), translations=(),
            examples=()):
        """

        :param value: The word itself.
        :type value: unicode
        :param parts:
            Other words, from which this is composed. (For example,
            Kinderzimmer is composed from Kind and Zimmer.)
        :type parts: iterable of :py:class:`words <Word>`
        :type examples: iterable of Example

        .. note::
            If ``value`` is not passed to constructor, that attribute is
            not created at all. (Because, for example, for class
            representing German verb attribute ``value`` can be
            meaningless.)

        """

        super(Word, self).__init__()

        if value is not None:
            self.value = value

        self.comment = comment
        self.part_of = IOBTree()
        self.parts = list(parts)
        self.meanings = list(translations)
        self.examples = IOBTree()
        for example in examples:
            self.examples[example.number] = example

    def __lt__(self, other):
        return unicode(self) < unicode(other)

    def _add_word_meanings(self, meaning, info):
        """ Adds word meanings.
        """

        word_meaning = WordMeaning(
                self, meaning, info[u'comment'], info[u'examples'])

        self.meanings.setdefault(
                info[u'translation'], []).append(word_meaning)
        self.meanings_date[word_meaning.get_date_key()
                ] = word_meaning
        self.tag_tree.assign(word_meaning, id_lower_bound=100000)
        word_meaning.add_tag(Tag(u'word.meaning'))
        meaning.add_word(self)
        log.debug(
                u'Word {0} has meaning \"{1}\".',
                unicode(self), word_meaning.meaning.value)

    def create_links(self, words, meanings):
        """
        This function is called, when all data is read from files, to
        create links between words.
        """

        if isinstance(self.parts, list):
            # Creating new.
            parts = self.parts
            self.parts = IOBTree()
            for info in parts:
                for word in words[info[u'child']]:
                    log.debug(
                            u'{0} is part of {1}.',
                            unicode(word), unicode(self))
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
            for info in translations:
                translation = info[u'translation']
                try:
                    meaning = meanings[translation]
                except KeyError:
                    meaning = Meaning(translation)
                    meanings[translation] = meaning
                self._add_word_meanings(meaning, info)
        else:
            # Updating.
            warnings.warn(u'Word updating is not implemented. Skipping.')

    def get_meanings(self):
        """ Meanings generator.
        """
        for word_meanings in self.meanings.values():
            for word_meaning in word_meanings:
                yield word_meaning

    def add_composed(self, word):
        """ Adds word, in which this word is part, to list.
        """

        self.part_of[word.get_id()] = word

    def remove_composed(self, word):
        """ Removes word, in which this word is part, from list.
        """

        del self.part_of[word.get_id()]

    def destroy(self):
        """ Prepares word for deleting.
        """

        for word in self.part_of.values():
            raise Exception((
                u'Cannot delete word, which is part of {0}.').format(
                    word.get_id()))
        self.parts_of = None

        for key, word in list(self.parts.items()):
            word.remove_composed(self)
            del self.parts[key]
        self.parts = None

        for key, word_meanings in list(self.meanings.items()):
            meanings = set()
            for word_meaning in word_meanings:
                self.tag_tree.unassign(word_meaning)
                meanings.add(word_meaning.meaning)
            for meaning in meanings:
                meaning.remove_word(self)
            del self.meanings[key]

        self.meanings_date = None

    def __unicode__(self):
        return u'{0.value} {1}'.format(self, self.get_id())


class XMLWordParser(object):
    """ Extracts information about Words.
    """

    words = None
    words_list = None
    meanings = None

    def __init__(self, manager, persistent_data):

        self.manager = manager
        if XMLWordParser.words is None:
            XMLWordParser.words = {}
            XMLWordParser.words_list = db.create_or_get(
                    persistent_data, u'words', IOBTree)
            XMLWordParser.meanings = db.create_or_get(
                    persistent_data, u'meanings', OOBTree)

        self.write = Writer().write

    def parse(self, node):
        """ Parses given ``word`` node.
        """

        object_id = int(node.get(u'id'))
        self.manager.mark_object_id(object_id)

        value = unicode(node.get(u'value', '')).strip()
        if len(value) == 0:
            raise Exception(u'Word value cannot be empty.')

        tags = TagList(unicode(node.get(u'tags', u'')))
        comment = unicode(node.get(u'comment', u''))

        translations = []
        parts = []
        examples = []
        for child in node:
            if child.tag == u'translation':
                translations.append({
                    u'translation': unicode(child.text),
                    u'comment': unicode(child.get(u'comment', u'')),
                    u'examples': [
                        int(nr)
                        for nr in child.get(u'examples', u'').split()],
                    })
            elif child.tag == u'part':
                parts.append({
                    u'child': unicode(child.text),
                    })
            elif child.tag == u'example':
                examples.append(Example(
                    int(child.attrib[u'nr']),
                    unicode(child.attrib[u'org']),
                    unicode(child.attrib[u'tr'])))

        tree = self.manager.get_tag_tree()

        try:
            word = tree.get_object(object_id)
            warnings.warn(u'Word updating is not implemented. Skipping.')
        except KeyError:
            word = Word(value, comment, parts, translations, examples)
            tree.assign(word, object_id)
            log.debug(u'TagTree counter: {0}.', tree._counter)
            for tag in tags:
                word.add_tag(tag)
            self.words_list[object_id] = word
            self.write(
                    u'{0}: \"{1}\" ({2})\n', (u'Adding', 'green'),
                    word.value, object_id)

        self.words.setdefault(value, []).append(word)

    def finalize(self):
        """ This function is called, when all data is parsed.
        """
        log.debug(u'Finalizing words: creating interlinks.')

        linked = set()
        for words in self.words.values():
            for word in words:
                if word.get_id() not in linked:
                    linked.add(word.get_id())
                    word.create_links(self.words, self.meanings)

        objects = set(self.words_list) - self.manager.object_id_set

        if objects:
            tree = self.manager.get_tag_tree()
            for object_id in objects:
                word = self.words_list[object_id]
                self.write(
                        u'{0}: \"{1}\"\n', (u'Deleting', 'red'),
                        word)
                word.destroy()
                tree.unassign(word)
                del self.words_list[object_id]


class WordPlugin(InformationHolderPlugin):
    """ Registering plugin.
    """

    tag_name = u'word'
    xml_parser = XMLWordParser
