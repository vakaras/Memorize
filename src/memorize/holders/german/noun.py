#!/usr/bin/python


""" Information holder for german nouns.
"""


import warnings

from memorize.log import Logger
from memorize.holders import word, InformationHolderPlugin
from memorize.tag_tree import TagList, Tag


log = Logger('memorize.holders.german.noun')


class NounMeaning(word.WordMeaning):
    """ The memorizable meaning of concrete noun.
    """

    def __unicode__(self):
        return u'NounMeaning {1}: {0.word} {0.meaning}'.format(
                self, self.get_id())


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
        if self.singular and info[u'number'] in (u'singular', u'both'):
            word_meanings.append((
                NounMeaning(
                    self, meaning, info[u'comment'], info['examples']),
                TagList((
                    u'word.noun.meaning.singular',
                    u'word.noun.meaning.{0}'.format(info[u'gender']))),
                ))
        if self.plural and info[u'number'] in (u'plural', u'both'):
            word_meanings.append((
                NounMeaning(
                    self, meaning, info[u'comment'], info['examples']),
                TagList((
                    u'word.noun.meaning.plural',
                    u'word.noun.meaning.{0}'.format(info[u'gender']))),
                ))
        for word_meaning, tags in word_meanings:
            self.meanings.setdefault(
                    info[u'translation'], []).append(word_meaning)
            self.meanings_date[word_meaning.get_date_key()
                    ] = word_meaning
            self.tag_tree.assign(word_meaning, id_lower_bound=100000)
            for tag in tags:
                word_meaning.add_tag(tag)
        meaning.add_word(self)


class XMLNounParser(word.XMLWordParser):
    """ Extracts information about Nouns.
    """

    def parse(self, node):
        """ Parses given ``noun`` node.
        """

        object_id = int(node.get(u'id'))
        self.manager.mark_object_id(object_id)

        genders = unicode(node.get(u'gender', '')).strip().split()
        if not genders:
            raise Exception(u'German noun gender must be specified.')
        singular = unicode(node.get(u'singular', '')).strip() or None
        plural = unicode(node.get(u'plural', '')).strip() or None
        if not singular and not plural:
            raise Exception(
                    u'At least one of singular or plural forms must '
                    u'be specified.')

        tags = TagList(unicode(node.get(u'tags', u'')))
        tags.append(u'word.noun')
        for gender in genders:
            tags.append([u'word', u'noun', gender])
        comment = unicode(node.get(u'comment', u''))

        translations = []
        parts = []
        examples = []
        for child in node:
            if child.tag == u'translation':
                if len(genders) == 1:
                    if 'gender' in child.attrib:
                        raise Exception(
                                u'Noun with one gender can\'t have '
                                u'translation with gender specified.')
                    else:
                        gender = genders[0]
                else:
                    gender = child.attrib['gender']
                    if gender not in genders:
                        raise Exception(
                                u'Translation gender can\'t differ '
                                u'from noun gender.'
                                )
                translations.append({
                    u'translation': unicode(child.get(u'value')),
                    u'comment': unicode(child.get(u'comment', u'')),
                    u'number': unicode(child.get(u'number', u'both')),
                    u'gender': gender,
                    u'examples': [
                        int(nr)
                        for nr in child.get(u'example', u'').split()],
                    })
            elif child.tag == u'part':
                parts.append({
                    u'child': unicode(child.get(u'value', u'')),
                    })
            elif child.tag == u'example':
                examples.append(word.Example(
                    int(child.attrib[u'nr']),
                    unicode(child.attrib[u'org']),
                    unicode(child.attrib[u'tr'])))

        tree = self.manager.get_tag_tree()

        try:
            noun = tree.get_object(object_id)
            warnings.warn(u'Word updating is not implemented. Skipping.')
        except KeyError:
            noun = Noun(
                    singular, plural, comment, parts, translations,
                    examples)
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
