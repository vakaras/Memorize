#!/usr/bin/python


""" :py:class:`TaggedObject` is a base class for all objects, which are
being to be stored in :py:class:`TagTree`.
"""


import persistent
from BTrees.OOBTree import OOBTree

from memorize.tag_tree.exceptions import IntegrityError
from memorize.tag_tree.tag import Tag


class TaggedObject(persistent.Persistent):
    """ Tagged object, which belongs to one or more tag nodes.

    .. warning::
        TaggedObject can be assigned just to one TagTree.

    >>> tree = TagTree()
    >>> tree2 = TagTree()
    >>> obj = TaggedObject()
    >>> tree.assign(obj)
    >>> tree2.assign(obj)
    ...
    IntegrityError: 'TaggedObject can belong just to one tree.'
    >>> a = Tag(u'a')
    >>> obj.add_tag(a)
    >>> tree.get(a)
    [<TaggedObject at ...>]
    >>> obj.remove_tag(a)
    >>> tree.get(a)
    []
    >>> tree.get(u'a.b')
    ...
    UknownTagError

    """

    def __init__(self):

        self._id = None
        self._tags = None               # Tag tuple to TagNode mapping.
        self._tag_tree = None

    def initialize(self, unique_id, tag_tree):
        """ This function is called, when object is assigned to Tree.
        """

        if self._tag_tree is not None:
            if self._tag_tree is tag_tree:
                raise IntegrityError(
                        u'TaggedObject is already assigned to TagTree.')
            else:
                raise IntegrityError(
                        u'TaggedObject can belong just to one TagTree.')
        else:
            self._id = unique_id
            self._tags = OOBTree()
            self._tag_tree = tag_tree

    def get_id(self):
        """ Returns unique id of the object.
        """

        if self._id is None:
            raise IntegrityError(
                    u'TaggedObject is not assigned to TagTree.')
        else:
            return self._id

    def add_tag(self, tag):
        """ Assigns tag to object.

        :param tag: memorize.tag_tree.Tag
        """

        if self._tag_tree is None:
            raise IntegrityError(
                    u'TaggedObject is not assigned to TagTree.')
        elif self._tags.has_key(tag.as_tuple()):
            raise KeyError(
                    u'TaggedObject is already tagged with {0}.'.format(
                        unicode(tag)))
        else:
            tag_node = self._tag_tree.get_tag_node(tag)
            tag_node.add_object(self)
            self._tags[tag.as_tuple()] = tag_node

    def remove_tag(self, tag):
        """ Removes tag from object.

        :param tag: memorize.tag_tree.Tag
        """

        try:
            del self._tags[tag.as_tuple()]
        except TypeError:
            raise IntegrityError(
                    u'TaggedObject is not assigned to TagTree.')
        except KeyError:
            raise KeyError(
                    u'TaggedObject is not tagged with {0}.'.format(
                        unicode(tag)))

    def get_tag_list(self):
        """ Returns a list of tags, by which this object is tagged.
        """

        return [Tag(tag) for tag in self._tags.keys()]
