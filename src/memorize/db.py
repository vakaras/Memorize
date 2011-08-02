#!/usr/bin/python


""" Settings and functions for connecting to ZODB.
"""


import os

from ZODB.FileStorage import FileStorage
from ZODB.DB import DB


HOME_DIRECTORY = os.getenv("HOME")
DATABASE_DIRECTORY = os.path.join(HOME_DIRECTORY, '.memorize')
DATABASE_PATH = os.path.join(DATABASE_DIRECTORY, 'data.fs')


def connect(path=DATABASE_PATH):
    """ Connects to database and returns its root.
    """

    storage = FileStorage(path)
    database = DB(storage)
    connection = database.open()

    return connection.root()


def create_or_get(container, key, create_cls):
    """ Returns element from dict like ``container`` object by ``key``.
    If entry referenced by ``key`` does not exist, then creates with
    ``create_cls``.

    :type container: dict like object
    """

    if not container.has_key(key):
        container[key] = create_cls()
    return container[key]
