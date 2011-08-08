#!/usr/bin/python


""" Manipulator for words.
"""


import datetime

from termcolor import colored

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

        write = lambda text, color='white': file.write(colored(text, color))

        # TODO: Show word and word meaning comments.
        write(u'Asking for word.\n')
        write(u'Tags assigned to word: ')
        write(
                u' '.join([
                    unicode(tag) for tag in self.word.get_tag_list()
                    ]),
                'green')
        write(u'\n')
        write(u'Word meaning: ')
        write(self.word_meaning.meaning.value, 'green')
        write(u'\n')

    def change_state(self, word, word_meaning, rating, write):
        """ Changes state of ``word_meaning``.
        """

        del word.meanings_date[word_meaning.get_date_key()]
        time = word_meaning.get_next_practice_unicode()
        word_meaning.plan(rating)
        word.meanings_date[word_meaning.get_date_key()] = word_meaning
        write(u'  {0} (times: {1}) -> {2}\n'.format(
            time, word_meaning._successfully_practiced,
            word_meaning.get_next_practice_unicode()))

    def parse_answer(self, answer, file):
        """ Parses user answer and prints response.

        .. todo::
            Write colorful printer, which has method:

            ``write(u'template', (obj, color), (obj, color),...)``.
        """

        log.debug(u'Parsing user answer')

        write = lambda text, color='white': file.write(colored(text, color))

        user_answers = [
                user_answer.strip() for user_answer in answer.split(u'|')]
        correct_answers = dict([
                (word.value, word)
                for word in self.word_meaning.meaning.get_word_list()])
        expected_answer = self.word.value


        # Evaluates answer.
        for user_answer in user_answers:
            if user_answer in correct_answers:
                # Informing user.
                write(u'  Correct answer \"')
                write(user_answer, 'green')
                write(u'\". All meanings:\n')
                for word_meaning in correct_answers[
                        user_answer].meanings.values():
                    write(u'    ')
                    write(word_meaning.meaning.value, 'green')
                    write(u'\n')
                # Changing state.
                word = correct_answers[user_answer]
                self.change_state(
                        word,
                        word.meanings[self.word_meaning.meaning.value],
                        5, write)
            else:
                # TODO: Search for word. Maybe mixed?
                write(u'  Incorrect answer \"')
                write(user_answer, 'red')
                write(u'\".\n')

        write(u'Expected answer was \"{0}\". '.format(expected_answer))
        if expected_answer in user_answers:
            write(u'Correct.\n', 'green')
        else:
            if not answer:
                write(u'No answer.\n', 'red')
                self.change_state(self.word, self.word_meaning, 0, write)
            else:
                write(u'Incorrect answer.\n', 'red')
                self.change_state(self.word, self.word_meaning, 1, write)

        # Shows additional information about word.

        if len(self.word.meanings) > 1:
            write(u'Other meanings of \"{0}\":\n'.format(self.word.value))
            for meaning in self.word.meanings:
                if meaning != self.word_meaning.meaning.value:
                    write(u'  {0}\n'.format(meaning), 'green')

        if len(self.word_meaning.meaning.words) > 1:
            write(u'Other words, which has meaning \"{0}\":\n'.format(
                self.word_meaning.meaning.value))
            for word in self.word_meaning.meaning.words.values():
                if not word is self.word:
                    write(u'  {0}\n'.format(word.value), 'green')

        write(u'\n')


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
            for meaning in word.meanings_date:
                log.debug(meaning)
            meaning = word.meanings_date.values()[0]
            if meaning.get_next_practice().date() <= today:
                self.questions.append(WordQuestion(
                    self, word, meaning))


    def get_questions(self):
        """ Returns list of ted questions.
        """

        log.debug(u'Returning generated questions list.')

        return self.questions
