#!/usr/bin/python


""" Information holder for german verbs.
"""


import warnings

import persistent

from memorize.memorizable import Memorizable
from memorize.log import Logger
from memorize.holders import word, InformationHolderPlugin
from memorize.tag_tree import TagList, Tag


log = Logger('memorize.holders.german.verb')


class VerbMeaning(word.WordMeaning):
    """ The memorizable meaning of concrete verb.
    """

    def __unicode__(self):
        return u'VerbMeaning {1}: {0.word} {0.meaning}'.format(
                self, self.get_id())


class ConjugationForm(Memorizable):
    """ The memorizable verb form.

    .. todo::
        Implement.
    """


class Verb(word.Word):
    """ German verb.
    """

    def __init__(self, infinitive, prefix, *args, **kwargs):
        super(Verb, self).__init__(None, *args, **kwargs)

        self.infinitive = infinitive
        self.prefix = prefix
        # TODO: self.conjugation =

    def __unicode__(self):
        if self.prefix:
            return u'{0.prefix}{0.infinitive} ({1})'.format(
                    self, self.get_id())
        else:
            return u'{0.infinitive} ({1})'.format(self, self.get_id())

    def _add_word_meanings(self, meaning, info):
        """ Adds word meanings.
        """

        word_meaning = VerbMeaning(
                self, meaning, info[u'comment'], info[u'examples'])

        self.meanings.setdefault(
                info[u'translation'], []).append(word_meaning)
        self.meanings_date[word_meaning.get_date_key()
                ] = word_meaning
        self.tag_tree.assign(word_meaning, id_lower_bound=100000)
        word_meaning.add_tag(Tag(u'word.verb.meaning'))
        meaning.add_word(self)
        log.debug(
                u'Verb {0} has meaning \"{1}\".',
                unicode(self), word_meaning.meaning.value)

    @property
    def full_infinitive(self):
        """ If verb has prefix, then returns prefix + infinitive,
        otherwise -- just infinitive.
        """
        if self.prefix:
            return self.prefix + self.infinitive
        else:
            return self.infinitive


class XMLVerbParser(word.XMLWordParser):
    """ Extracts information about Verbs.
    """

    def parse(self, node):
        """ Parses given ``verb`` node.
        """

        object_id = int(node.get(u'id'))
        self.manager.mark_object_id(object_id)

        infinitive = unicode(node.get(u'infinitive', u'')).strip()
        if not infinitive:
            raise Exception(u'Verb infinitive form must be specified.')
        prefix = node.get(u'prefix')
        if prefix:
            prefix = unicode(prefix).strip()

        tags = TagList(unicode(node.get(u'tags', u'')))
        tags.append(u'word.verb')
        transitiveness = node.get(u'transitiveness')
        if transitiveness == u'transitive':
            tags.append(u'word.verb.transitive')
        elif transitiveness == u'intransitive':
            tags.append(u'word.verb.intransitive')
        elif transitiveness == u'both':
            tags.append(u'word.verb.transitive')
            tags.append(u'word.verb.intransitive')
        else:
            raise Exception(u'Verb transitiveness must be specified.')
        comment = unicode(node.get(u'comment', u''))

        translations = []
        parts = []
        examples = []
        for child in node:
            if child.tag == u'translation':
                translations.append({
                    u'translation': unicode(child.get(u'value')),
                    u'comment': unicode(child.get(u'comment', u'')),
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
            verb = tree.get_object(object_id)
            warnings.warn(u'Word updating is not implemented. Skipping.')
        except KeyError:
            verb = Verb(
                    infinitive, prefix, comment, parts, translations,
                    examples)
            tree.assign(verb, object_id)
            log.debug(u'TagTree counter: {0}.', tree._counter)
            for tag in tags:
                verb.add_tag(tag)
            self.words_list[object_id] = verb
            self.write(u'{0}: {1}\n', (u'Adding', 'green'), unicode(verb))

        if prefix:
            self.words.setdefault(prefix + infinitive, []).append(verb)
        else:
            self.words.setdefault(infinitive, []).append(verb)

    def finalize(self):
        """ Already finalized in Word.
        """


class VerbPlugin(InformationHolderPlugin):
    """ Registering plugin.
    """

    tag_name = u'verb'
    xml_parser = XMLVerbParser
