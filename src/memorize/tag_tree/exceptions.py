#!/usr/bin/python


""" All custom exceptions, which can be thrown by :py:class:`TagTree`.
"""


class TagTreeError(Exception):
    """ The basic exception for all :py:class:`TagTree` exceptions.
    """


class IntegrityError(TagTreeError):
    """ :py:class:`TagTree` integrity check failed.
    """
