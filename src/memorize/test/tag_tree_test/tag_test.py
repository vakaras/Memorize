#!/usr/bin/python
# -*- encoding: utf-8 -*-


""" Tests for memorize.tags.
"""


import unittest


from memorize.tag_tree import Tag, TagList
from memorize.tag_tree.exceptions import IntegrityError


class TagTest(unittest.TestCase):
    """ Tests for Tag.
    """

    def test_conversions(self):

        self.assertRaises(TypeError, Tag, 'a')
        self.assertRaises(TypeError, Tag, ['a'])

        a = Tag(u'a')
        self.assertEqual(a.levels, [u'a'])
        self.assertEqual(a.as_tuple(), (u'a',))
        self.assertEqual(a.as_unicode(), u'a')
        self.assertEqual(unicode(a), u'a')

        ab = Tag(u'ą.b̃')
        self.assertEqual(ab.levels, [u'ą', u'b̃'])
        self.assertEqual(ab.as_tuple(), (u'ą', u'b̃'))
        self.assertEqual(ab.as_unicode(), u'ą.b̃')
        self.assertEqual(ab.as_unicode(u'|'), u'ą|b̃')
        self.assertEqual(unicode(ab), u'ą.b̃')

        t = (u'a', u'b', u'c', u'd', u'e')
        v = Tag(t)
        self.assertEqual(v.levels, [u'a', u'b', u'c', u'd', u'e'])
        for i1, i2 in zip(t, v):
            self.assertEqual(i1, i2)

        self.assertEqual(Tag(u'a'), Tag(u'a'))
        self.assertNotEqual(Tag(u'a'), Tag(u'b'))

        self.assertRaises(IntegrityError, Tag, u'')
        self.assertRaises(IntegrityError, Tag, [u'', u''])
        self.assertRaises(IntegrityError, Tag, [])


class TagsListTest(unittest.TestCase):
    """ Tests for TestList.
    """

    def test_conversions(self):

        self.assertRaises(TypeError, TagList, 'a')
        self.assertRaises(TypeError, TagList, ['a'])
        self.assertRaises(TypeError, TagList, [['a']])

        a = TagList(u'a')
        self.assertEqual([t.levels for t in a.tags], [[u'a']])
        self.assertEqual(a.as_unicode(), u'a')
        self.assertEqual(unicode(a), u'a')
        self.assertEqual(list(a), [Tag(u'a')])

        b = TagList(u'\n  b \n    ')
        self.assertEqual([t.levels for t in b.tags], [[u'b']])
        self.assertEqual(b.as_unicode(), u'b')
        self.assertEqual(unicode(b), u'b')
        self.assertEqual(list(b), [Tag(u'b')])

        u = TagList(u'a.b \n\n    a.c  \n\n a.b.c\n\n')
        self.assertEqual(
                [t.levels for t in u.tags],
                [[u'a', u'b'], [u'a', u'c'], [u'a', u'b', u'c']])
        self.assertEqual(u.as_unicode(), u'a.b a.c a.b.c')
        self.assertEqual(u.as_unicode(u':', u'|'), u'a|b:a|c:a|b|c')
        self.assertEqual(unicode(u), u'a.b a.c a.b.c')
        self.assertEqual(
                list(u),
                [Tag(u'a.b'), Tag(u'a.c'), Tag(u'a.b.c')])
