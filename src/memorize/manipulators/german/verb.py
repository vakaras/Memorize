#!/usr/bin/python


""" Manipulator for german verbs.
"""


import datetime

from memorize.log import Logger
from memorize.utils import Writer
from memorize.manipulators import ManipulatorPlugin
from memorize.tag_tree import TagList, Tag
from memorize.manipulators import word


log = Logger('memorize.manipulators.german.verb')


class VerbQuestion(word.WordQuestion):
    """ Question object for verb.
    """

    def show(self, file):
        """ Prints question to a file.
        """

        log.debug(u'Showing WordQuestion.')

        write = Writer(file).write

        write(u'Asking for German verb.\n')
        if self.word.comment:
            write(u'Word comment: {0}\n', self.word.comment)
        if self.word_meaning.examples:
            write(u'Examples:\n')
            for nr in self.word_meaning.examples:
                write(
                        u'  {0.number}. {0.translation}\n',
                        self.word.examples[nr])
        words = len(self.word_meaning.meaning.get_word_list())
        if words > 1:
            write(u'{0} words have this meaning. ', words)
        write(u'Word meaning: {0}\n',
              (self.word_meaning.meaning.value, 'green'))
        if self.word_meaning.comment:
            write(u'Meaning comment: {0}\n', self.word_meaning.comment)
        write(u'Word meaning tags: {0}.\n',
                (u' '.join([
                    unicode(tag)
                    for tag in self.word_meaning.get_tag_list()
                    ]),
                    'green'))

    def check_answer(self, user_answer, write):
        """ Checks if user answer is correct.
        """
        correct = False
        for verb in self.word_meaning.meaning.get_word_list():
            if verb.full_infinitive == user_answer:
                write(u'  Correct answer \"{0}\". All meanings:\n',
                      (user_answer, 'green'))
                write(u'    ({0})\n',
                      u' '.join([
                          unicode(tag)
                          for tag in verb.get_tag_list()
                          ]))
                for translation in verb.meanings:
                    write(u'    {0}\n', (translation, 'green'))
                correct = True
        if correct:
            return True
        else:
            write(u'  Incorrect answer \"{0}\".\n', (user_answer, 'red'))
            return False

    def parse_answer(self, answer, file):
        """ Parses user answer and prints response.
        """

        log.debug(u'Parsing user answer')

        writer = Writer(file)
        write = writer.write

        user_answers = [
                user_answer.strip() for user_answer in answer.split(u'|')]
        for user_answer in user_answers:
            self.check_answer(user_answer, write)
        if self.word.prefix:
            expected_answer = self.word.prefix + self.word.infinitive
        else:
            expected_answer = self.word.infinitive

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

        if len(self.word.meanings) > 1:
            write(u'All meanings of \"{0}\":\n', unicode(self.word))
            for translation in self.word.meanings:
                write(u'  {0}\n', (translation, 'green'))
        write(u'Tags assigned to word: {0}\n',
              (u' '.join([
                  unicode(tag) for tag in self.word.get_tag_list()]),
               'green',))

        if len(self.word_meaning.meaning.words) > 1:
            write(u'Other words, which have meaning \"{0}\":\n',
                  self.word_meaning.meaning.value)
            for word in self.word_meaning.meaning.words.values():
                if not word is self.word:
                    write(u'  {0} ({1})\n',
                          (unicode(word), 'green'),
                          u' '.join([
                              unicode(tag)
                              for tag in self.word.get_tag_list()
                              ]))
        write(u'\n')

        if self.word.parts:
            write(u'Parts:\n')
            for word in self.word.parts.values():
                write(u'  {0}\n', word)
                for translation in word.meanings:
                    write(u'    {0}\n', translation)
        if self.word_meaning.examples:
            write(u'Examples:\n')
            for nr in self.word_meaning.examples:
                write(
                        (u'  {0.number}. {0.translation}\n'
                        u'     {0.original}\n'),
                        self.word.examples[nr])


class VerbFormQuestion:
    """ Question object for verb form.
    """

    def __init__(self, manipulator, word, form, old_date):
        log.debug(u'Constructing WordQuestion.')

        self.manipulator = manipulator
        self.word = word
        self.form = form
        self.old_date = old_date

    def show(self, file):
        """ Prints question to a file.
        """

        write = Writer(file).write

        write(u'Asking for German verb form.\n')
        if self.word.comment:
            write(u'Word comment: {0}\n', self.word.comment)
        if self.word.examples:
            for example in self.word.examples.values():
                write(u'  {0.number}. {0.translation}\n', example)
        if len(self.word.meanings) > 1:
            write(u'All meanings of \"{0}\":\n', unicode(self.word))
            for translation in self.word.meanings:
                write(u'  {0}\n', (translation, 'green'))
        write(u'Verb infinitive: {0}.\n',
                (self.word.full_infinitive, 'green'))
        write(u'Required form: {0}.\n', (u' '.join(self.form.key), 'green'))
        write(u'Verb form tags: {0}.\n',
                (u' '.join([
                    unicode(tag)
                    for tag in self.form.get_tag_list()
                    ]),
                    'green'))

    def parse_answer(self, answer, file):
        """ Parses user answer and prints response.
        """

        log.debug(u'Parsing user answer')

        writer = Writer(file)
        write = writer.write

        write(u'Expected answer was \"{0}\". ', self.form.value)
        if answer.strip() == self.form.value:
            writer.write_string(u'Correct.\n', 'green')
            self.change_state(self.word, self.form, 5, write)
        else:
            if not answer:
                writer.write_string(u'No answer.\n', 'red')
                self.change_state(self.word, self.form, 0, write)
            else:
                writer.write_string(u'Incorrect answer.\n', 'red')
                self.change_state(self.word, self.form, 1, write)
        if self.word.examples:
            for example in self.word.examples.values():
                write(
                        (u'  {0.number}. {0.translation}\n'
                        u'    {0.original}\n'), example)


    def change_state(self, verb, verb_form, rating, write):
        """ Changes state of ``verb_form``.
        """

        del verb.conjugation_forms_date[self.old_date]
        time = verb_form.get_next_practice_unicode()
        verb_form.plan(rating)
        verb.conjugation_forms_date[verb_form.get_date_key()] = verb_form
        write(u'  {0} (times: {1}) -> {2}\n'.format(
            time, verb_form._successfully_practiced,
            verb_form.get_next_practice_unicode()))


class VerbManipulatorPlugin(ManipulatorPlugin):
    """ Manipulator which generates questions for verbs.
    """

    def __init__(self, plugin_manager):
        log.debug(u'Called verb manipulator constructor.')
        super(VerbManipulatorPlugin, self).__init__(plugin_manager)

        self.plugin_manager = plugin_manager

        # Collects words.
        tags = (
                u'word.verb.transitive',
                u'word.verb.intransitive',)
        self.words = set()
        for tag in tags:
            self.words.update(
                    self.plugin_manager.tag_tree.get_objects(
                        TagList((tag,))))

        # FIXME: Wet code.
        # Creates questions.
        today = datetime.date.today()
        self.questions = []
        for word in self.words:
            log.debug(u'Collected word: {0}', word)
            for date, meaning in word.meanings_date.items():
                if meaning.get_next_practice().date() <= today:
                    self.questions.append(VerbQuestion(
                        self, word, meaning, date))
                    log.debug(u'Added meaning: {0}.', date)
                else:
                    break
            for date, form in word.conjugation_forms_date.items():
                if form.get_next_practice().date() <= today:
                    self.questions.append(VerbFormQuestion(
                        self, word, form, date))
                    log.debug(u'Added form: {0}.', date)
                else:
                    break

    def get_questions(self):
        """ Returns list of ted questions.
        """

        log.debug(u'Returning generated questions list.')

        return self.questions
