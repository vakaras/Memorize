#!/usr/bin/python


""" Tests for memorize.tag_tree.tagged_object.
"""


import unittest


from memorize.tag_tree import Tag, TaggedObject
from memorize.tag_tree.exceptions import IntegrityError


class TaggedObjectTest(unittest.TestCase):
    """ Tests for TaggedObject.
    """

    def test_uninitialized(self):

        o = TaggedObject()

        self.assertRaises(IntegrityError, o.get_id)
        self.assertRaises(IntegrityError, o.add_tag, Tag(u'a'))
        self.assertRaises(IntegrityError, o.remove_tag, Tag(u'a'))

    def test_initialization(self):

        class DummyTree(object):
            """ Dummy TagTree.
            """

        tree1 = DummyTree()
        tree2 = DummyTree()

        o = TaggedObject()

        o.initialize(1, tree1)
        self.assertRaises(IntegrityError, o.initialize, 1, tree1)
        self.assertRaises(IntegrityError, o.initialize, 1, tree2)


    def test_initialized(self):

        class DummyNode(object):
            """ Dummy TagNode.
            """

            def add_object(self, obj):
                pass

        class DummyTree(object):
            """ Dummy TagTree.
            """

            parent = self

            def get_tag_node(self, tag):
                DummyTree.parent.assertEqual(tag, Tag(u'a.b'))
                return DummyNode()

        tree = DummyTree()
        o = TaggedObject()
        o.initialize(1, tree)

        self.assertEqual(o.get_id(), 1)
        o.add_tag(Tag([u'a', u'b']))
        self.assertRaises(KeyError, o.add_tag, Tag([u'a', u'b']))
        self.assertEqual(o.get_tag_list(), [Tag(u'a.b')])
        o.remove_tag(Tag([u'a', u'b']))
        self.assertRaises(KeyError, o.remove_tag, Tag([u'a', u'b']))
