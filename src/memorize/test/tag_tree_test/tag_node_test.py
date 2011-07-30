#!/usr/bin/python


""" Tests for memorize.tag_tree.tag_node.
"""


import unittest


from memorize.tag_tree import Tag, TaggedObject
from memorize.tag_tree.tag_node import TagNode
from memorize.tag_tree.exceptions import IntegrityError


class TagNodeTest(unittest.TestCase):
    """ Tests for TagNode.
    """

    def test_manipulation(self):

        root = TagNode(name=None)

        a = root.create_child_node(u'a')
        self.assertRaises(KeyError, root.create_child_node, u'a')
        self.assertRaises(KeyError, root.get_child_node, u'b')
        self.assertIs(a, root.get_child_node(u'a'))
        self.assertRaises(KeyError, root.delete_child_node, u'b')
        root.delete_child_node(u'a')
        self.assertRaises(KeyError, root.get_child_node, u'a')

        node = root
        for level in Tag(u'a.b.c.d'):
            node = node.create_child_node(level)
        self.assertEqual(node.get_tag(), Tag(u'a.b.c.d'))

        class DummyTree(object):
            """ A dummy TagTree.
            """

        tree = DummyTree()

        class A(TaggedObject):

            def __init__(self, unique_id, name):
                self._id = unique_id
                self._tag_tree = tree
                self.name = name

            def get_id(self):
                return self._id

        o1 = A(1, u'root:1')
        o2 = A(2, u'root:2')

        root.add_object(o1)
        root.add_object(o2)
        self.assertRaises(KeyError, root.add_object, o2)
        self.assertIs(o1, root.get_object(1))
        root.remove_object(o1)
        root.remove_object(2)
