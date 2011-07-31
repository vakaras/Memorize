#!/usr/bin/python


""" Tests for memorize.tag_tree.tag_tree.
"""


import unittest


from memorize.tag_tree import Tag, TagList, TaggedObject, TagTree
from memorize.tag_tree.tag_node import TagNode
from memorize.tag_tree.exceptions import IntegrityError


class TagTreeTest(unittest.TestCase):
    """ Tests for TaggedObject.
    """

    def test_everything(self):

        tree = TagTree()

        tag = Tag(u'a.a.a.a.a')
        tree.create_tag(tag)
        node = tree.get_tag_node(tag)
        self.assertEqual(node.get_tag(), tag)
        tree.delete_tag(Tag(u'a.a'))
        self.assertRaises(KeyError, tree.get_tag_node, Tag(u'a.a'))

        tree.create_tag(Tag(u'a.b.c.d'))
        tree.create_tag(Tag(u'a.e.f'))
        tree.create_tag(Tag(u'a.e.g'))
        tree.create_tag(Tag(u'h'))

        node = tree.get_tag_node(Tag(u'a.b.c.d'))

        objects = [TaggedObject() for i in range(10)]
        for obj, tag in zip(
                objects,
                [
                    u'a', u'a.b', u'a.b.c', u'a.b.c.d', u'a.e', u'a.e.f',
                    u'a.e.g', u'h', u'a.b.c.d']):
            tree.assign(obj)
            obj.add_tag(Tag(tag))
        objects[8].add_tag(Tag(u'a.e.f'))
        self.assertRaises(KeyError, objects[8].add_tag, Tag(u'h.e.f'))

        # Generated Tree:
        #             root
        #         a1            h8
        #     b2      e5
        #     c3    f69 g7
        #     d49

        self.assertTrue(objects[8].has_tag(Tag(u'a.e.f')))
        self.assertTrue(objects[8].has_tag(Tag(u'a.b.c.d')))
        self.assertTrue(objects[6].has_tag(Tag(u'a.e.g')))
        self.assertTrue(objects[6].has_tag(Tag(u'a.e')))
        self.assertTrue(objects[6].has_tag(Tag(u'a')))
        self.assertFalse(objects[6].has_tag(Tag(u'b')))

        self.assertEqual(
                sorted([
                    unicode(tag) for tag in objects[8].get_tag_list()]),
                [u'a.b.c.d', u'a.e.f'])

        self.assertEqual(
              sorted([o.get_id() for o in tree.get_objects(Tag(u'a'))]),
              list(range(1, 8)) + [9])
        self.assertEqual(
              sorted([
                  o.get_id()
                  for o in tree.get_tag_node(Tag(u'a')).get_object_list()]),
              list(range(1, 8)) + [9])
        self.assertEqual(
              sorted([
                  o.get_id()
                  for o in tree.get_tag_node(Tag(u'a')
                      ).get_object_list(Tag(u'e'))]),
              [5, 6, 7, 9])
        self.assertEqual(
              sorted([
                  o.get_id()
                  for o in tree.get_objects(
                      Tag(u'a'), lambda x: x.get_id() > 3)]),
              [4, 5, 6, 7, 9])
        self.assertEqual(
              sorted([
                  o.get_id()
                  for o in tree.get_objects(TagList([u'a.b.c', u'a.e']))]),
              [9])

        self.assertEquals(
                sorted([unicode(tag) for tag in objects[8].get_tag_list()]),
                [u'a.b.c.d', u'a.e.f'])
        tree.delete_tag(Tag(u'a.e'))
        self.assertEquals(
                sorted([unicode(tag) for tag in objects[8].get_tag_list()]),
                [u'a.b.c.d'])
