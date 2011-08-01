#!/usr/bin/python


"""
Mount point for all information holders.
"""


from memorize.plugins import MountPoint


class InformationHolderPlugin(object):
    """ Base class for any plugin, which implements information
    holders.

    Plugin manager will look for these attributes:

    +   `xml_parser` -- class, which can be used to create and update
        information holders.
    """

    __metaclass__ = MountPoint
