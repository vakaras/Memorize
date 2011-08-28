#!/usr/bin/python


""" Container, which allows objects access by tags.
"""


import persistent
from BTrees.IOBTree import IOBTree

from memorize.tag_tree.exceptions import IntegrityError
from memorize.tag_tree.tag import Tag
from memorize.tag_tree.tag_node import TagNode


class TagTree(persistent.Persistent):
    """ Container, which allows objects access by tags.
    """

    def __init__(self):
        self._root = TagNode(name=None)
        self._objects = IOBTree()
        self._counter = 1               # Unique object id generator.

    def create_tag(self, tag):
        """ Creates all TagNode's needed to store objects tagged by
        ``tag``.

        :type tag: Tag
        """

        node = self._root
        for level in tag:
            try:
                node = node.get_child_node(level)
            except KeyError:
                node = node.create_child_node(level)

    def delete_tag(self, tag):
        """ Deletes TagNode referenced by ``tag``.

        :type tag: Tag

        .. todo::
            Deleting TagNode should untag all objects, which are tagged
            by it and its children.
        """

        node = self._root
        for level in tag:
            parent = node
            node = node.get_child_node(level)
        parent.delete_child_node(level)

    def assign(self, obj, object_id=None):
        """ Assigns object to tree.

        If object_id is not given, then generates an unique one.
        """

        object_id = int(object_id) if object_id is not None else None

        if object_id is None:
            obj.initialize(self._counter, self)
            self._objects[self._counter] = obj
            self._counter += 1
        elif self._objects.has_key(object_id):
            raise IntegrityError(
                    u'Object with id {0} already exists.'.format(object_id))
        else:
            obj.initialize(object_id, self)
            self._objects[object_id] = obj
            self._counter = max(self._counter, object_id + 1)

    def unassign(self, obj):
        """ Unassigns object from tree.
        """

        if not obj is self._objects[obj.get_id()]:
            raise IntegrityError(
                    u'Object is not assigned to this tree.')
        else:
            object_id = obj.get_id()
            obj.uninitialize()
            del self._objects[object_id]

    def get_tag_node(self, tag):
        """ Returns TagNode by tag.
        """
        node = self._root
        for level in tag:
            node = node.get_child_node(level)
        return node

    def get_objects(self, tags, filter=lambda x: True):
        """ Returns all objects, which are tagged by ``tags`` and passes
        filter.

        :type tags: Tag or TagList
        """

        if isinstance(tags, Tag):
            node = self.get_tag_node(tags)
            tags = []
        else:
            node = self.get_tag_node(list(tags).pop())

        objects = []
        for obj in node.get_object_list(None, filter):
            if all([obj.has_tag(tag) for tag in tags]):
                objects.append(obj)
        return objects

    def get_object(self, object_id):
        """ Returns object by its id.

        .. todo::
            Create tests. (Unit and Doc.)
        """

        return self._objects[object_id]
