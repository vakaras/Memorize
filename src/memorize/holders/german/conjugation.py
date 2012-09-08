#!/usr/bin/python
# -*- coding: utf-8 -*-


from memorize.log import Logger


log = Logger('memorize.holders.german.verb.conjugation')


def is_vowel(letter):
    """ Returns True if letter is a vowel.
    """
    if letter.isalpha() and len(letter) == 1:
        return letter.lower() in u'aäeioöuü'
    else:
        raise ValueError(u'{0} is not a letter.'.format(letter))


def is_consonant(letter):
    """ Returns True if letter is a consonant.
    """
    return not is_vowel(letter)


def is_kranton(stem):
    """ Returns True if stem is kranto stem.
    """
    if stem.endswith(u'd') or stem.endswith(u't'):
        return True
    elif stem.endswith(u'n') or stem.endswith(u'm'):
        if is_vowel(stem[-2]):
            return False
        elif is_vowel(stem[-3]):
            if stem[-2] == stem[-1]:
                return False
            elif stem[-2] in u'lrh':
                return False
            else:
                return True
        else:
            return True
    else:
        return False


class Present(object):
    """ Forms of present tense.

    Algorithm description is
    `here <http://www.cambridgeclarion.org/gremple/german.verb.conjugation.html>`_
    """

    def __init__(self, infinitive, stem, is_kranton, conjugation_data):
        self.infinitive = infinitive
        self.stem = stem
        self.is_kranton = is_kranton
        self.conjugation_data = conjugation_data.get(u'present', {})

    def __iter__(self):
        for pronoun in (u'ich', u'du', u'es', u'wir', u'ihr', u'sie'):
            yield (pronoun, getattr(self, pronoun))

    @property
    def ich(self):
        try:
            return self.conjugation_data[u'ich']
        except KeyError:
            if self.infinitive.endswith(u'eln'):
                return self.infinitive[:-3] + u'le'
            else:
                return self.stem + u'e'

    @property
    def du(self):
        try:
            return self.conjugation_data[u'du']
        except KeyError:
            if u'es' in self.conjugation_data:
                stem = self.conjugation_data[u'es'][:-1]
            else:
                stem = self.stem
            if self.is_kranton:
                return stem + u'est'
            elif stem.endswith(u'ss') or stem[-1] in u'sßxz':
                return stem + u't'
            else:
                return stem + u'st'

    @property
    def es(self):
        try:
            return self.conjugation_data[u'es']
        except KeyError:
            if self.is_kranton:
                return self.stem + u'et'
            else:
                return self.stem + u't'

    @property
    def wir(self):
        try:
            return self.conjugation_data[u'wir']
        except KeyError:
            return self.infinitive

    @property
    def ihr(self):
        try:
            return self.conjugation_data[u'ihr']
        except KeyError:
            if self.is_kranton:
                return self.stem + u'et'
            else:
                return self.stem + u't'

    @property
    def sie(self):
        return self.wir


class Past(object):
    """ Forms of past tense.

    Algorithm description is
    `here <http://www.cambridgeclarion.org/gremple/german.verb.conjugation.html>`_
    """

    def __init__(self, infinitive, stem, is_kranton, conjugation_data):
        self.infinitive = infinitive
        self.is_kranton = is_kranton
        self.conjugation_data = conjugation_data.get(u'past', {})
        self.stem = stem
        if u'es' in self.conjugation_data:
            self.beginning = self.conjugation_data[u'es']
        elif is_kranton:
            self.beginning = self.stem + u'ete'
        else:
            self.beginning = self.stem + u'te'

    def __iter__(self):
        for pronoun in (u'ich', u'du', u'es', u'wir', u'ihr', u'sie'):
            yield (pronoun, getattr(self, pronoun))

    @property
    def ich(self):
        try:
            return self.conjugation_data[u'ich']
        except KeyError:
            return self.beginning

    @property
    def du(self):
        try:
            return self.conjugation_data[u'du']
        except KeyError:
            if is_kranton(self.beginning):
                return self.beginning + u'est'
            else:
                return self.beginning + u'st'

    @property
    def es(self):
        return self.beginning

    @property
    def wir(self):
        try:
            return self.conjugation_data[u'wir']
        except KeyError:
            if self.beginning.endswith(u'te'):
                return self.beginning + u'n'
            else:
                return self.beginning + u'en'

    @property
    def ihr(self):
        try:
            return self.conjugation_data[u'ihr']
        except KeyError:
            if is_kranton(self.beginning):
                return self.beginning + u'et'
            else:
                return self.beginning + u't'

    @property
    def sie(self):
        return self.wir


class Conjugator:
    """ Conjugates German verb.
    """

    def __init__(self, infinitive, conjugation_data):
        self.infinitive = infinitive
        self.conjugation_data = conjugation_data
        self.present = Present(
                self.infinitive, self.stem, self.is_kranton(),
                self.conjugation_data)
        self.past = Past(
                self.infinitive, self.stem, self.is_kranton(),
                self.conjugation_data)

    @property
    def stem(self):
        """ Returns stem of verb.

        Algorithm described
        `here <http://www.cambridgeclarion.org/gremple/german.verb.conjugation.html#stem>`_
        """

        if self.infinitive == u'knien':
            return u'knie'
        elif self.infinitive.endswith(u'en'):
            return self.infinitive[:-2]
        else:
            return self.infinitive[:-1]

    @property
    def infinitive_ending(self):
        """ Returns ending of infinitive.

        Algorithm described
        `here <http://www.cambridgeclarion.org/gremple/german.verb.conjugation.html#stem>`_
        """
        return self.infinitive[len(self.stem):]

    def is_kranton(self):
        """ Returns True if stem is kranto stem.
        """
        return is_kranton(self.stem)
