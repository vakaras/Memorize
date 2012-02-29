#!/usr/bin/python


""" Information holder for german nouns.
"""


import warnings

from memorize.log import Logger
from memorize.holders import word, InformationHolderPlugin
from memorize.tag_tree import TagList


log = Logger('memorize.holders.german.noun')


class NounMeaning(word.WordMeaning):
    """ The memorizable meaning of concrete noun.
    """

    def __init__(self, meaning, form, comment):
        """
        :type form: u'singular' or u'plural'.
        """
        super(NounMeaning, self).__init__(meaning, comment)
        self.form = form


class Noun(word.Word):
    """ German noun.
    """

    def __init__(self, singular, plural, *args, **kwargs):
        """

        :param singular: Singular form of noun.
        :type singular: Unicode or None.
        :param plural: Plural form of noun.
        :type plural: Unicode or None.

        Other arguments are passed to Word.
        """

        super(Noun, self).__init__(None, *args, **kwargs)

        self.singular = singular
        self.plural = plural

    def __unicode__(self):
        return u'{0.singular} {0.plural} ({1})'.format(self, self.get_id())

    def _add_word_meanings(self, meaning, info):
        """ Adds word meanings.
        """

        word_meanings = []
        if self.singular:
            word_meanings.append(
                    NounMeaning(meaning, u'singular', info[u'comment']))
        if self.plural:
            word_meanings.append(
                    NounMeaning(meaning, u'plural', info[u'comment']))
        for word_meaning in word_meanings:
            self.meanings.setdefault(
                    info[u'translation'], []).append(word_meaning)
            self.meanings_date[word_meaning.get_date_key()
                    ] = word_meaning
        meaning.add_word(self)


class XMLNounParser(word.XMLWordParser):
    """ Extracts information about Nouns.
    """

    def parse(self, node):
        """ Parses given ``noun`` node.
        """

        object_id = int(node.get(u'id'))
        self.manager.mark_object_id(object_id)

        gender = unicode(node.get(u'gender', '')).strip()
        if not gender:
            raise Exception(u'German noun gender must be specified.')
        singular = unicode(node.get(u'singular', '')).strip() or None
        plural = unicode(node.get(u'plural', '')).strip() or None
        if not singular and not plural:
            raise Exception(
                    u'At least one of singular or plural forms must '
                    u'be specified.')

        tags = TagList(unicode(node.get(u'tags', u'')))
        tags.append(u'word.noun')
        tags.append([u'word', u'noun', gender])
        comment = unicode(node.get(u'comment', u''))

        translations = []
        parts = []
        for child in node:
            if child.tag == u'translation':
                translations.append({
                    u'translation': unicode(child.get(u'value')),
                    u'comment': unicode(child.get(u'comment', u'')),
                    # TODO: Add translation tag.
                    # TODO: Add example tag.
                    })
            elif child.tag == u'part':
                parts.append({
                    u'child': unicode(child.get(u'value', u'')),
                    })

        tree = self.manager.get_tag_tree()

        try:
            noun = tree.get_object(object_id)
            warnings.warn(u'Word updating is not implemented. Skipping.')
        except KeyError:
            noun = Noun(singular, plural, comment, parts, translations)
            tree.assign(noun, object_id)
            log.debug(u'TagTree counter: {0}.', tree._counter)
            for tag in tags:
                noun.add_tag(tag)
            self.words_list[object_id] = noun
            self.write(
                    u'{0}: \"{1}\" \"{2}\" ({3})\n', (u'Adding', 'green'),
                    noun.singular, noun.plural, object_id)

        if singular:
            self.words.setdefault(singular, []).append(noun)
        if plural:
            self.words.setdefault(plural, []).append(noun)

    def finalize(self):
        """ Already finalized in Word.
        """


class NounPlugin(InformationHolderPlugin):
    """ Registering plugin.
    """

    tag_name = u'noun'
    xml_parser = XMLNounParser
