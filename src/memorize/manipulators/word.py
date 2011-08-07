#!/usr/bin/python


""" Manipulator for words.
"""


import datetime

from memorize.log import Logger
from memorize.manipulators import ManipulatorPlugin
from memorize.tag_tree import TagList


log = Logger('memorize.manipulators.word')


class WordQuestion(object):
    """ Question object for word.
    """

    def __init__(self, manipulator, word, word_meaning):
        log.debug(u'Constructing WordQuestion.')

        self.manipulator = manipulator
        self.word = word
        self.word_meaning = word_meaning


    def show(self, file):
        """ Prints question to file.
        """
        log.debug(u'Showing WordQuestion.')

    def parse_answer(self, answer, file):
        """ Parses user answer and prints response.
        """
        log.debug(u'Parsing user answer')


class WordManipulatorPlugin(ManipulatorPlugin):
    """ Manipulator which generates questions for words.
    """

    def __init__(self, plugin_manager):

        log.debug(u'Called word manipulator constructor.')
        super(WordManipulatorPlugin, self).__init__(plugin_manager)

        self.plugin_manager = plugin_manager

        # Collects words.
        self.words = self.plugin_manager.tag_tree.get_objects(
                TagList(u'word'))

        # Creates questions.
        today = datetime.date.today()
        self.questions = []
        for word in self.words:
            log.debug(u'Collected word: {0}', word.value)
            # TODO: Find out, what is better: to ask one meaning at a time
            # or all.
            meaning = word.meanings_date.values()[0]
            if meaning.get_next_practice().date() <= today:
                self.questions.append(WordQuestion(
                    self, word, meaning))


    def get_questions(self):
        """ Returns list of ted questions.
        """

        log.debug(u'Returning generated questions list.')

        return self.questions
