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

        a = root.get_child_node(u'a')
        b = a.get_child_node(u'b')
        c = b.get_child_node(u'c')
        d = c.get_child_node(u'd')

        e = a.create_child_node(u'e')
        f = e.create_child_node(u'f')
        g = e.create_child_node(u'g')
        h = root.create_child_node(u'h')

        a.add_object(A(1, u'a:1'))
        b.add_object(A(2, u'a.b:2'))
        c.add_object(A(3, u'a.b.c:3'))
        d.add_object(A(4, u'a.b.c.d:4'))
        e.add_object(A(5, u'a.e:5'))
        f.add_object(A(6, u'a.e.f:6'))
        g.add_object(A(7, u'a.e.g:7'))
        h.add_object(A(8, u'h:8'))

        o = A(9, u'a.b.c.d a.e.f : 9')
        d.add_object(o)
        f.add_object(o)

        # Generated Tree:
        #             root
        #         a1            h8
        #     b2      e5
        #     c3    f69 g7
        #     d49

        self.assertEqual(d.get_tag(), Tag(u'a.b.c.d'))
        self.assertEqual(f.get_tag(), Tag(u'a.e.f'))
        self.assertEqual(g.get_tag(), Tag(u'a.e.g'))
        self.assertEqual(h.get_tag(), Tag(u'h'))

        self.assertEqual(
                sorted([o.get_id() for o in root.get_object_list()]),
                list(range(1, 10)))
        self.assertEqual(
                sorted([
                    o.get_id()
                    for o in root.get_object_list(
                        filter=lambda x: x.get_id() > 4)
                    ]),
                list(range(5, 10)))

        self.assertEqual(
                sorted([
                    o.get_id()
                    for o in root.get_object_list(
                        Tag(u'a.b'))]),
                [2, 3, 4, 9])
