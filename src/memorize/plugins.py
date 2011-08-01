#!/usr/bin/python


""" Plugin architecture based on idea described
`here <http://martyalchin.com/2008/jan/10/simple-plugin-framework/>`_.
"""


class MountPoint(type):
    """ Base class for plugin mount point.
    """

    def __init__(cls, name, bases, attrs):
        """
        +   If creating mount point class, then creates plugins list.
        +   If creating plugin, then ads it to plugins list.

        """

        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)
