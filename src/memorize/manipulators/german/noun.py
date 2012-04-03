#!/usr/bin/python


""" Manipulator for german nouns.
"""


import datetime

from memorize.log import Logger
from memorize.utils import Writer
from memorize.manipulators import ManipulatorPlugin
from memorize.tag_tree import TagList, Tag
from memorize.manipulators import word


log = Logger('memorize.manipulators.german.noun')


def nominative(noun, word_meaning=None):
    """ Forms nominative singular form of noun.
    """

    if word_meaning is None:
        tagged_object = noun
        tag_template = u'word.noun.{0}'
    else:
        tagged_object = word_meaning
        tag_template = u'word.noun.meaning.{0}'

    articles = {
            u'feminine': u'die',
            u'masculine': u'der',
            u'neuter': u'das',
            }

    for gender, article in articles.items():
        if tagged_object.has_tag(Tag(tag_template.format(gender))):
            return u'{0} {1}'.format(article, noun.singular)
    else:
        raise Exception(u'Unknown noun gender. Tags: {0}.'.format(
            u' '.join(
                unicode(tag) for tag in tagged_object.get_tag_list())))


class NounQuestion(word.WordQuestion):
    """ Question object for noun.
    """

    BLACKLISTED_TAGS = (
            u'word.noun.meaning.feminine',
            u'word.noun.meaning.masculine',
            u'word.noun.meaning.neuter',
            )

    def show(self, file):
        """ Prints question to file.
        """

        log.debug(u'Showing WordQuestion.')

        write = Writer(file).write

        write(u'Asking for german noun.\n')
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
                    if unicode(tag) not in self.BLACKLISTED_TAGS
                    ]),
                    'green'))

    def check_answer(self, user_answer, write):
        """ Checks if user answer is correct.
        """
        correct = False
        for noun in self.word_meaning.meaning.get_word_list():
            if ((self.word_meaning.has_tag(
                Tag(u'word.noun.meaning.singular')) and
                    nominative(noun) == user_answer) or
                (self.word_meaning.has_tag(
                    Tag(u'word.noun.meaning.plural')) and
                    noun.plural == user_answer)):
                write(u'  Correct answer \"{0}\". All meanings:\n',
                      (user_answer, 'green'))
                write(u'    ({0})\n',
                      u' '.join([
                          unicode(tag)
                          for tag in noun.get_tag_list()
                          ]))
                for translation in noun.meanings:
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
        if self.word_meaning.has_tag(Tag(u'word.noun.meaning.singular')):
            expected_answer = nominative(self.word, self.word_meaning)
        else:
            expected_answer = self.word.plural

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
        write(u'Word meaning tags: {0}.\n',
                (u' '.join([
                    unicode(tag)
                    for tag in self.word_meaning.get_tag_list()
                    ]),
                    'green'))

        if len(self.word_meaning.meaning.words) > 1:
            write(u'Other words, which have meaning \"{0}\":\n',
                  self.word_meaning.meaning.value)
            for word in self.word_meaning.meaning.words.values():
                if not word is self.word:
                    write(u'  {0} ({1})\n',
                          (unicode(word), 'green'),
                          u' '.join([
                              unicode(tag)
                              for tag in word.get_tag_list()
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


class NounManipulatorPlugin(ManipulatorPlugin):
    """ Manipulator which generates questions for nouns.
    """

    def __init__(self, plugin_manager):
        log.debug(u'Called noun manipulator constructor.')
        super(NounManipulatorPlugin, self).__init__(plugin_manager)

        self.plugin_manager = plugin_manager

        # Collects words.
        tags = (
                u'word.noun.feminine',
                u'word.noun.masculine',
                u'word.noun.neuter',)
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
                    self.questions.append(NounQuestion(
                        self, word, meaning, date))
                    log.debug(u'Added meaning: {0}.', date)
                else:
                    break

    def get_questions(self):
        """ Returns list of ted questions.
        """

        log.debug(u'Returning generated questions list.')

        return self.questions
