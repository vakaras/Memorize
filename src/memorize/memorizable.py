#!/usr/bin/python


""" Memorizable information.
"""

from datetime import datetime, timedelta
from random import randrange

import persistent


def get_now():
    """ Returns time of the moment + some random delta < 1 hour.
    """

    return datetime.now() + timedelta(seconds=randrange(3600))


class Memorizable(persistent.Persistent):
    """ Base class for memorizable information.
    """

    def __init__(self):
        self._successfully_practiced = 1
        self._easy_factor = 2.5
        self._next_practice = get_now()

    def plan(self, rating):
        """ Plan next practice.

        :param rating: Rating of user answer.
        :type rating: One of 1, 2, 3, 4, 5.
        """

        delay_days, self._easy_factor = self.count_delay(
                self._successfully_practiced, rating, self._easy_factor)
        if rating > 3:
            # If practice was successful.
            self._successfully_practiced += 1
        self._next_practice = get_now() + timedelta(days=delay_days)

    def count_delay(self, times_practiced, rating, easy_factor):
        """ Calculates how many days to delay question.

        Used Algorithm is described
        `here <http://www.supermemo.com/english/ol/sm2.htm>`_.
        """

        new_easy_factor = (
                easy_factor +
                (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)))
        if new_easy_factor < 1.3:
            new_easy_factor = 1.3

        if rating < 3:
            return 1, new_easy_factor
        elif times_practiced == 1:
            return 1, new_easy_factor
        elif times_practiced == 2:
            return 6, new_easy_factor

        delay_days, new_easy_factor = self.count_delay(
                times_practiced-1, rating, easy_factor)
        return delay_days * easy_factor, new_easy_factor

    def get_next_practice(self):
        """ Returns time of next practice.
        """

        return self._next_practice

    def get_next_practice_unicode(self):
        """ Returns time of next practice as unicode string.
        """

        return self._next_practice.strftime(u'%Y-%m-%d %H:%M:%S')
