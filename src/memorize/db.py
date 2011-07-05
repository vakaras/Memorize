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

    storage = FileStorage(DATABASE_PATH)
    db = DB(storage)
    connection = db.open()

    return connection.root()
