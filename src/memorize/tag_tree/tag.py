#!/usr/bin/python


""" Converters to and from various representations of tags.
"""


import re

from memorize.tag_tree.exceptions import IntegrityError


DEFAULT_TAG_LEVEL_SEPARATOR_RE = u'\.'  # Have to be valid regexp value!
DEFAULT_TAG_LEVEL_SEPARATOR = u'.'
DEFAULT_TAGS_SEPARATOR_RE = u'\s*'      # Any amount of whitespace.


class Tag(object):
    """ Object which represents tag.
    """

    def __init__(
            self, tag,
            re_separator=DEFAULT_TAG_LEVEL_SEPARATOR_RE,
            separator=DEFAULT_TAG_LEVEL_SEPARATOR,
            ):
        """

        :type tag: unicode string or iterable of unicode strings.
        :param re_separator:
            If tag is unicode, then it is split by using regular expression
            separator.
        :param separator: Used to join levels to unicode string.

        """

        self.re_separator = re_separator
        self.separator = separator

        if isinstance(tag, unicode):
            self.levels = re.split(self.re_separator, tag, flags=re.UNICODE)
        else:
            self.levels = []
            for level in tag:
                if isinstance(level, unicode):
                    self.levels.append(level)
                else:
                    raise TypeError(
                            u'Tag level have to be an unicode string.')

        if not self.levels:
            raise IntegrityError(u'Tag cannot be empty!')
        for level in self.levels:
            if len(level) == 0:
                raise IntegrityError(u'Tag level cannot be empty!')

    def as_tuple(self):
        """ Returns tag as tuple of unicode strings.
        """

        return tuple(self.levels)

    def as_unicode(self, separator=None):
        """ Returns tag as unicode string.

        If separator is None, then separator, which was passed to
        constructor, is used.
        """

        return (separator or self.separator).join(self.levels)

    def __unicode__(self):
        return self.as_unicode()

    def __iter__(self):
        """ Iterator through tag levels.
        """

        return iter(self.levels)

    def __eq__(self, tag):
        return self.levels == tag.levels

    def __ne__(self, tag):
        return self.levels != tag.levels


class TagList(object):
    """ Object which represents a list of tags.
    """

    def __init__(
            self, tags,
            re_levels_separator=DEFAULT_TAG_LEVEL_SEPARATOR_RE,
            levels_separator=DEFAULT_TAG_LEVEL_SEPARATOR,
            re_tags_separator=DEFAULT_TAGS_SEPARATOR_RE,
            ):
        """

        :type tag:
            unicode string or iterable of unicode strings or iterable of
            iterables of unicode strings.
        :param re_levels_separator: If tag is unicode, then it is split to
            levels using this regular expression.
        :param levels_separator: Used to join levels to unicode string.
        :param re_tags_separator: If tag is unicode, then it is split using
            this regular expression.

        """

        self.re_levels_separator = re_levels_separator
        self.levels_separator = levels_separator
        self.re_tags_separator = re_tags_separator

        if isinstance(tags, unicode):
            self.tags = [
                    Tag(tag)
                    for tag in re.split(
                        self.re_tags_separator, tags, flags=re.UNICODE)
                    if len(tag) > 0]
        else:
            self.tags = [Tag(tag) for tag in tags]

    def as_unicode(self, tags_separator=u' ', levels_separator=None):
        """ Returns tag as unicode string.
        """

        return tags_separator.join([
            tag.as_unicode(levels_separator) for tag in self.tags])

    def __unicode__(self):
        return self.as_unicode()

    def __iter__(self):
        """ Iterator through tags.
        """

        return iter(self.tags)
