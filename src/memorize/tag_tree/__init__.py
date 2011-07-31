#!/usr/bin/python


"""
:py:class:`TagTree <memorize.tag_tree.tag_tree.TagTree>` is a data
structure, which allows to access objects by tags associated with them.

All classes of objects to be stored in
:py:class:`TagTree <memorize.tag_tree.tag_tree.TagTree>` have to
inherit from
:py:class:`TaggedObject <memorize.tag_tree.tagged_object.TaggedObject>`.
Example:

>>> from memorize.tag_tree import TaggedObject
>>> class Word(TaggedObject):
...     def __init__(self, value):
...         super(Word, self).__init__()
...         self.value = value
>>> word = Word(u'hello')

Object before using have to be assigned to tree:

>>> from memorize.tag_tree import TagTree
>>> tree = TagTree()
>>> tree.assign(word)

Creating tags in TagTree:

>>> from memorize.tag_tree import Tag
>>> tree.create_tag(Tag(u'a.b.c'))
>>> tree.create_tag(Tag(u'a.b.d'))

Tagging object:

>>> word.add_tag(Tag(u'a.b'))

Getting objects by tag:

>>> tree.get_objects(Tag(u'a'))[0] is word
True
>>> tree.get_objects(Tag(u'a.b'))[0] is word
True
>>> tree.get_objects(Tag(u'a.b.c')) == []
True

A more complicated example:

>>> words = []
>>> for i in range(10):
...     word = Word(unicode(i))
...     tree.assign(word)
...     words.append(word)
>>> for tag in [u'a.b.c', u'a.b.d.e', u'a.b.d.f', u'h']:
...     tree.create_tag(Tag(tag))
>>> words[0].add_tag(Tag(u'a'))
>>> words[1].add_tag(Tag(u'a'))
>>> words[5].add_tag(Tag(u'a.b'))
>>> words[6].add_tag(Tag(u'a.b'))
>>> words[8].add_tag(Tag(u'a.b.c'))
>>> words[3].add_tag(Tag(u'a.b.c'))
>>> words[5].add_tag(Tag(u'a.b.c'))
>>> words[4].add_tag(Tag(u'a.b.d'))
>>> words[7].add_tag(Tag(u'a.b.d'))
>>> words[3].add_tag(Tag(u'a.b.d.e'))
>>> words[9].add_tag(Tag(u'a.b.d.e'))
>>> words[1].add_tag(Tag(u'a.b.d.f'))
>>> words[4].add_tag(Tag(u'h'))

Genearated tag tree:

.. graphviz::

    digraph tree {
        "root" -> "a: 0, 1" -> "b: 5, 6, hello" -> "c: 8, 3, 5";
        "b: 5, 6, hello" -> "d: 4, 7" -> "e: 3, 9";
        "d: 4, 7" -> "f: 1";
        "root" -> "h: 4";
        }

>>> from memorize.tag_tree import TagList
>>> def show_result(tags, filter=lambda x: True):
...     objects = tree.get_objects(
...         tags, filter=filter)
...     for value in sorted([obj.value for obj in objects]):
...         print 'word:', value
...
>>> show_result(TagList(u'a.b h'))
word: 4
>>> show_result(TagList(u'a.b'))
word: 1
word: 3
word: 4
word: 5
word: 6
word: 7
word: 8
word: 9
word: hello
>>> show_result(TagList(u'a.b'), lambda x: x.value > u'2')
word: 3
word: 4
word: 5
word: 6
word: 7
word: 8
word: 9
word: hello
>>> show_result(TagList(u'a.b.c a.b.d.f'), lambda x: x.value > u'2')
>>> show_result(TagList(u'a.b.c a.b.d.e'), lambda x: x.value > u'2')
word: 3

"""


from memorize.tag_tree.tag import Tag, TagList
from memorize.tag_tree.tagged_object import TaggedObject
from memorize.tag_tree.tag_tree import TagTree
