#!/usr/bin/python


""" Tests for memorize.db.
"""


import unittest


from memorize.db import connect


def test_connection():
    """ Test for ``connect``.
    """

    root = connect()
    root["a"] = 1
