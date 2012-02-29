#!/usr/bin/python


""" Manipulator for words.
"""


import datetime

from memorize.log import Logger
from memorize.utils import Writer
from memorize.manipulators import ManipulatorPlugin
from memorize.tag_tree import TagList


log = Logger('memorize.manipulators.word')


class WordQuestion(object):
    """ Question object for word.
    """

    def __init__(self, manipulator, word, word_meaning, old_date):
        log.debug(u'Constructing WordQuestion.')

        self.manipulator = manipulator
        self.word = word
        self.word_meaning = word_meaning
        self.old_date = old_date

    def show(self, file):
        """ Prints question to file.
        """

        log.debug(u'Showing WordQuestion.')

        write = Writer(file).write

        write(u'Asking for word.\n')
        write(u'Tags assigned to word: {0}\n',
              (u' '.join([
                  unicode(tag) for tag in self.word.get_tag_list()]),
               'green',))
        if self.word.comment:
            write(u'Word comment: {0}\n', self.word.comment)
        words = len(self.word_meaning.meaning.get_word_list())
        if words > 1:
            write(u'{0} words have this meaning. ', words)
            different_words = len(set([
                word.value
                for word in self.word_meaning.meaning.get_word_list()]))
            if different_words == words:
                write(u'All of them are different.\n')
            else:
                write(u'{0} of them are different.\n', different_words)
        write(u'Word meaning: {0}\n',
              (self.word_meaning.meaning.value, 'green'))
        if self.word_meaning.comment:
            write(u'Meaning comment: {0}\n', self.word_meaning.comment)
        if self.word_meaning.examples:
            write(u'Examples:\n')
            for nr in self.word_meaning.examples:
                write(
                        u'  {0.number}. {0.translation}\n',
                        self.word.examples[nr])

    def change_state(self, word, word_meaning, rating, write):
        """ Changes state of ``word_meaning``.
        """

        del word.meanings_date[self.old_date]
        time = word_meaning.get_next_practice_unicode()
        word_meaning.plan(rating)
        word.meanings_date[word_meaning.get_date_key()] = word_meaning
        write(u'  {0} (times: {1}) -> {2}\n'.format(
            time, word_meaning._successfully_practiced,
            word_meaning.get_next_practice_unicode()))

    def parse_answer(self, answer, file):
        """ Parses user answer and prints response.

        .. todo::
            Print all meanings of the word. (For example "scribe", can
            be both noun and verb, so it is holded in two information
            holders. But it would be better to print all its meanings
            anyway.)

        .. todo::
            Show usage examples.
        """

        log.debug(u'Parsing user answer')

        writer = Writer(file)
        write = writer.write

        user_answers = [
                user_answer.strip() for user_answer in answer.split(u'|')]
        correct_answers = {}
        for word in self.word_meaning.meaning.get_word_list():
            correct_answers.setdefault(word.value, []).append(word)
        expected_answer = self.word.value

        # Evaluates answer.
        for user_answer in user_answers:
            if user_answer in correct_answers:
                # Informing user.
                write(u'  Correct answer \"{0}\". All meanings:\n',
                      (user_answer, 'green'))
                for correct_answer in correct_answers[user_answer]:
                    write(u'    ({0})\n',
                          u' '.join([
                              unicode(tag)
                              for tag in correct_answer.get_tag_list()
                              ]))
                    for word_meaning in correct_answer.get_meanings():
                        write(u'    {0}\n',
                              (word_meaning.meaning.value, 'green'))
            else:
                # TODO: Search for word. Maybe mixed?
                write(u'  Incorrect answer \"{0}\".\n',
                      (user_answer, 'red'))

        write(u'Expected answer was \"{0}\". ', expected_answer)
        if expected_answer in user_answers:
            writer.write_string(u'Correct.\n', 'green')
            self.change_state(self.word, self.word_meaning, 5, write)
        else:
            if not answer:
                writer.write_string(u'No answer.\n', 'red')
                self.change_state(self.word, self.word_meaning, 0, write)
            else:
                writer.write_string(u'Incorrect answer.\n', 'red')
                self.change_state(self.word, self.word_meaning, 1, write)

        # Shows additional information about word.

        if len(self.word.meanings) > 1:
            write(u'All meanings of \"{0}\":\n', self.word.value)
            for meaning in self.word.meanings:
                write(u'  {0}\n', (meaning, 'green'))

        if len(self.word_meaning.meaning.words) > 1:
            write(u'Other words, which have meaning \"{0}\":\n',
                  self.word_meaning.meaning.value)
            for word in self.word_meaning.meaning.words.values():
                if not word is self.word:
                    write(u'  {0} ({1})\n',
                          (word.value, 'green'),
                          u' '.join([
                              unicode(tag)
                              for tag in self.word.get_tag_list()
                              ]))

        write(u'\n')
        if self.word_meaning.examples:
            write(u'Examples:\n')
            for nr in self.word_meaning.examples:
                write(
                        (u'  {0.number}. {0.translation}\n'
                        u'     {0.original}\n'),
                        self.word.examples[nr])


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
            for date, meaning in word.meanings_date.items():
                if meaning.get_next_practice().date() <= today:
                    self.questions.append(WordQuestion(
                        self, word, meaning, date))
                    log.debug(u'Added meaning: {0}.', date)
                else:
                    break

    def get_questions(self):
        """ Returns list of ted questions.
        """

        log.debug(u'Returning generated questions list.')

        return self.questions
