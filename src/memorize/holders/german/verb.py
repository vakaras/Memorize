#!/usr/bin/python


""" Information holder for german verbs.
"""


import warnings

import persistent
from BTrees.OOBTree import OOBTree

from memorize.memorizable import Memorizable
from memorize.log import Logger
from memorize.holders import word, InformationHolderPlugin
from memorize.tag_tree import TagList, Tag
from memorize.holders.german.conjugation import Conjugator


log = Logger('memorize.holders.german.verb')


class VerbMeaning(word.WordMeaning):
    """ The memorizable meaning of concrete verb.
    """

    def __unicode__(self):
        return u'VerbMeaning {1}: {0.word} {0.meaning}'.format(
                self, self.get_id())


class ConjugationForm(Memorizable):
    """ The memorizable verb form.
    """

    def __init__(self, verb, key, value):
        super(ConjugationForm, self).__init__()
        self.verb = verb
        self.key = key
        self.value = value

    def __unicode__(self):
        return u'ConjugationForm {1}: {0.verb} {0.key}'.format(
                self, self.get_id())

    def get_date_key(self):
        """ Returns key for use in ``conjugation_forms_date`` dictionary.
        """

        return u' -*- '.join([
            self.get_next_practice_unicode(),
            self.value,
            unicode(id(self))])

class Verb(word.Word):
    """ German verb.
    """

    def __init__(self, infinitive, prefix, conjugation_data,
            *args, **kwargs):
        super(Verb, self).__init__(None, *args, **kwargs)

        self.infinitive = infinitive
        self.prefix = prefix
        self.conjugation_forms = OOBTree()
        self.conjugation_forms_date = OOBTree()

        self._conjugator = Conjugator(prefix, infinitive, conjugation_data)

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
        word_meaning.add_tag(
                Tag(u'word.verb.meaning.{0}'.format(
                    info[u'transitiveness'])))
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

    def destroy(self):
        """ Prepares word for deleting.
        """
        super(Verb, self).destroy()
        for key, form in list(self.conjugation_forms.items()):
            self.tag_tree.unassign(form)
            del self.conjugation_forms[key]

    def create_links(self, words, meanings):
        """
        This function is called, when all data is read from files, to
        create links between words.
        """
        super(Verb, self).create_links(words, meanings)
        if self._conjugator is None:
            warnings.warn(u'Word updating is not implemented. Skipping.')
        else:
            for tag_list, key, value in self._conjugator.items():
                form = ConjugationForm(self, key, value)
                self.tag_tree.assign(form, id_lower_bound=100000)
                for tag in tag_list:
                    form.add_tag(tag)
                self.conjugation_forms[key] = form
                self.conjugation_forms_date[form.get_date_key()] = form
            self._conjugator = None


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
        if node.attrib[u'regularity'] == u'regular':
            tags.append(u'word.verb.regular')
        else:
            tags.append(u'word.verb.irregular')
        comment = unicode(node.get(u'comment', u''))

        translations = []
        parts = []
        examples = []
        conjugation_data = {}
        for child in node:
            if child.tag == u'translation':
                if transitiveness == u'both':
                    if 'transitiveness' in child.attrib:
                        translation_transitiveness = child.get(
                                'transitiveness')
                    else:
                        raise Exception(
                                u'Verb, which "transitiveness" is '
                                u'set to "both", must have transitiveness '
                                u'set for each meaning explicitly.')
                else:
                    translation_transitiveness = transitiveness
                translations.append({
                    u'translation': unicode(child.get(u'value')),
                    u'comment': unicode(child.get(u'comment', u'')),
                    u'examples': [
                        int(nr)
                        for nr in child.get(u'example', u'').split()],
                    u'transitiveness': translation_transitiveness,
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
            elif child.tag == u'present':
                conjugation_data[u'present'] = dict(child.attrib.items())
            elif child.tag == u'past':
                conjugation_data[u'past'] = dict(child.attrib.items())
            elif child.tag == u'perfect':
                conjugation_data[u'perfect'] = dict(child.attrib.items())

        tree = self.manager.get_tag_tree()

        try:
            verb = tree.get_object(object_id)
            warnings.warn(u'Word updating is not implemented. Skipping.')
        except KeyError:
            verb = Verb(
                    infinitive, prefix, conjugation_data, comment,
                    parts, translations, examples)
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
