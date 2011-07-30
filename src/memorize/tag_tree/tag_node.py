#!/usr/bin/python


""" :py:class:`TaggedNode` is a node of :py:class:`TagTree`.
"""


import persistent
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree

from memorize.tag_tree.tag import Tag


class TagNode(persistent.Persistent):
    """ Node of TagTree.
    """

    def __init__(self, name, parent=None):
        """
        :param name:
            Name of this TaggedNode. (Not a full name.) None means
            that this node is a root of tree.
        :type name: unicode or None
        :param parent: Parent node of this.
        :type parent: TagNode
        """

        self._name = name
        self._parent = parent
        self._children = OOBTree()
        self._objects = IOBTree()

    def destroy(self):
        """ Untags all objects, tagged by this TagNode, and also destroys
        all children recursively.
        """

        for node in self._children.values():
            node.destroy()

        tag = self.get_tag()
        for obj in list(self._objects.values()):
            obj.remove_tag(tag)

    def get_parent(self):
        """ Returns parent node.
        """
        return self._parent

    def get_name(self):
        """ Returns name (tag level) of this node.
        """
        return self._name

    def create_child_node(self, name):
        """ Creates and returns child node.
        """

        if self._children.has_key(name):
            raise KeyError(
                    u'TagNode already has child with name {0}.'.format(
                        name))
        else:
            self._children[name] = TagNode(name, self)
            return self._children[name]

    def delete_child_node(self, name):
        """ Deletes child node.
        """

        if not self._children.has_key(name):
            raise KeyError(
                    u'TagNode does not have child with name {0}.'.format(
                        name))
        else:
            self._children[name].destroy()
            del self._children[name]

    def get_child_node(self, name):
        """ Returns child node.
        """

        try:
            return self._children[name]
        except KeyError:
            raise KeyError(
                    u'TagNode does not have child with name {0}.'.format(
                        name))

    def get_tag(self):
        """ Returns :py:class:`Tag`, which this node represents.
        """

        levels = []
        node = self
        while node.get_parent():
            levels.append(node.get_name())
            node = node.get_parent()
        return Tag(reversed(levels))

    def add_object(self, obj):
        """ Adds object to tagged objects list.
        """

        if self._objects.has_key(obj.get_id()):
            raise KeyError(u'Object already tagged.')
        else:
            self._objects[obj.get_id()] = obj

    def remove_object(self, obj):
        """ Removes object from tagged objects list.

        :param obj: TaggedObject id or TaggedObject itself.
        """

        if isinstance(obj, int):
            del self._objects[obj]
        else:
            del self._objects[obj.get_id()]

    def get_object(self, object_id):
        """ Returns object by its id.
        """

        return self._objects[object_id]

    def get_object_dict(self, tag, filter):
        """ Returns dict (id->object) of all children nodes objects tagged
        with tag for which filter returns True.

        If ``tag`` is None, returns all objects (nodes and its children)
        which pass filter.

        :type tag: list of unicode strings or None
        """

        if tag is None or len(tag) == 0:
            # Collect all objects.
            objects = dict([
                (obj.get_id(), obj)
                for obj in self._objects.values() if filter(obj)])
            for node in self._children.values():
                objects.update(node.get_object_dict(None, filter))
            return objects
        else:
            # Recursively call child node.
            name = tag.pop()
            return self._children[name].get_object_dict(tag, filter)

    def get_object_list(self, tag=None, filter=lambda x: True):
        """ Returns list of all objects which passes tag and filter.

        +   If ``tag`` is None, returns all objects, which passes filter.
        +   Otherwise returns objects, which belongs to child TagNode
            with full name ``tag``, and which passes filter.

        :type tag: Tag or None
        """

        if tag is None:
            return self.get_object_dict(tag, filter).values()
        else:
            return self.get_object_dict(
                    list(reversed(tag.as_tuple())), filter).values()
