#!/usr/bin/python


""" **Memorize** is a program, which purpose is to help memorize
foreign language words.
"""


import sys
import argparse
import random
import datetime

import transaction

from memorize.log import Logger
from memorize.config import ConfigManager
from memorize.parsers import ParsersManager
from memorize.manipulators import ManipulatorsManager
from memorize.tag_tree import TagList, Tag


log = Logger('memorize', root=True)


def update_db(config, args):
    """ Updates ZODB.
    """

    log.info(u'Starting update.')

    log.info(u'Tagging NounMeaning with gender.')
    gender_tags = [
            Tag(u'word.noun.meaning.{0}'.format(gender))
            for gender in (u'feminine', u'masculine', u'neuter')]
    def is_tagged(noun_meaning):
        """ Checks if NounMeaning is tagged with gender.
        """
        for gender_tag in gender_tags:
            if noun_meaning.has_tag(gender_tag):
                return True
        else:
            return False
    for noun_meaning in config.tag_tree.get_objects(
            TagList(u'word.noun.meaning')):
        if is_tagged(noun_meaning):
            log.debug(u'Already tagged {0}.', noun_meaning)
        else:
            word = noun_meaning.word
            for gender in (u'feminine', u'masculine', u'neuter'):
                if word.has_tag(Tag(u'word.noun.{0}'.format(gender))):
                    tag = Tag(u'word.noun.meaning.{0}'.format(gender))
                    noun_meaning.add_tag(tag)
                    log.debug(u'{0} tagged with {1}.', noun_meaning, tag)
                    break
            else:
                raise Exception(u'Gender is not specified for {0}'.format(
                    word))
    del noun_meaning

    log.info(u'Tagging VerbMeaning with transitiveness.')
    t_tag = Tag(u'word.verb.meaning.transitive')
    i_tag = Tag(u'word.verb.meaning.intransitive')
    for verb_meaning in config.tag_tree.get_objects(
            TagList(u'word.verb.meaning')):
        if (verb_meaning.has_tag(t_tag) or
            verb_meaning.has_tag(i_tag)):
            log.debug(u'Already tagged {0}.', verb_meaning)
        else:
            word = verb_meaning.word
            if word.has_tag(Tag(u'word.verb.transitive')):
                verb_meaning.add_tag(t_tag)
                log.debug(u'{0} tagged with {1}.', verb_meaning, t_tag)
            elif word.has_tag(Tag(u'word.verb.intransitive')):
                verb_meaning.add_tag(i_tag)
                log.debug(u'{0} tagged with {1}.', verb_meaning, i_tag)
            else:
                raise Exception(
                        u'Transitiveness is not specified for {0}'.format(
                            word))

    if raw_input(u'Commit changes [y/N]:') == u'y':
        transaction.commit()
        log.info(u'Changes committed.')
    else:
        transaction.abort()
        log.info(u'Changes aborted.')


def sync(config, args):
    """ Synchronizes ZODB with XML.

    .. todo::
        Tags have to be sourced before any other data!
    """

    log.info(u'Starting synchronization.')

    manager = ParsersManager(config)
    for file in manager.collect():
        manager.parse_file(file)
    manager.finalize()

    if raw_input(u'Commit changes [y/N]:') == u'y':
        transaction.commit()
        log.info(u'Changes committed.')
    else:
        transaction.abort()
        log.info(u'Changes aborted.')


def collect(tag_tree, tags):
    """ Collects tagged objects.
    """
    objects = set()
    for tag in tags:
        objects.update(tag_tree.get_objects(TagList((tag,))))
    return objects


def print_word(word):
    """ Prints word info.
    """
    print(u'"{0}";"{1}";"{2}"'.format(
        word,
        u' '.join(unicode(tag) for tag in word.get_tag_list()),
        u'; '.join(
            translation for translation in word.meanings)).encode('utf-8'))


def dump_unlearned(config, args):
    """ Dumps unlearned words for next 2 days.
    """
    until = datetime.date.today() + datetime.timedelta(days=2)
    nouns = collect(
            config.tag_tree,
            (u'word.noun.feminine',
                u'word.noun.masculine',
                u'word.noun.neuter',))
    verbs = collect(
            config.tag_tree,
            (u'word.verb.transitive', u'word.verb.intransitive',))
    for word in sorted(nouns | verbs):
        for word_meaning in word.meanings_date.values():
            if word_meaning.get_next_practice().date() <= until:
                print_word(word)
                break


def give_lesson(config, args):
    """ Gives a lesson.
    """

    log.info(u'Creating lesson.')

    manager = ManipulatorsManager(config)
    manager.init_manipulators()
    questions = manager.collect_questions()
    if not questions:
        sys.stdout.write(u'No questions.\n'.encode('utf-8'))
    random.shuffle(questions)

    log.info(u'Lesson created.')

    sys.stdout.write((
        u'Questions for today: {0}.\n'.format(len(questions))
        ).encode('utf-8'))

    separator = '-' * 60 + '\n'
    try:
        for question in questions:
            sys.stdout.write(separator)
            question.show(sys.stdout)
            answer = raw_input(u'Answer: ').decode('utf-8')
            question.parse_answer(answer, sys.stdout)
            transaction.commit()
            log.info(u'Changes committed.')
    except (EOFError, KeyboardInterrupt):
        sys.stdout.write("\nLesson canceled.\n")

    log.info(u'Lesson finished.')


def get_free_id(config, args):
    """ Prints smallest unused object id.
    """

    print config.tag_tree._counter


def show_words(config, args):
    """ Prints all words.
    """
    tags = TagList((u'word',))
    for word in config.tag_tree.get_objects(tags):
        print unicode(word).encode('utf-8'),
        print unicode(TagList(word.get_tag_list())).encode('utf-8')


def show_meanings(config, args):
    """ Prints all meanings.
    """
    meanings = config.db_root[u'parsers_data']['word']['meanings']
    for meaning in meanings.values():
        print unicode(meaning).encode('utf-8')
        for word_id, word in meaning.words.items():
            print u'  {0} {1}'.format(word_id, word).encode('utf-8')


def main(argv=sys.argv[1:]):
    """ Main entry point.

    .. todo::
        Make all commands plugable.
    .. todo::
        Make command, which allows search between words. For example,
        what is the meaning of "foster"?
    .. todo::
        Log start and end times of the lesson.
    .. todo::
        Log how many times were answered correctly in lesson.
    .. todo::
        If istead of answer get something like: "/query", then
        do search between words with query. After the results
        show question again.
    """

    commands = {
            'sync': sync,
            'lesson': give_lesson,
            'getid': get_free_id,
            'show': show_words,
            'show_meanings': show_meanings,
            'update_db': update_db,
            'dump_unlearned': dump_unlearned,
            }

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
            u'-c', u'--config', metavar=u'CONFIG_FILE', type=file,
            dest='config_file', help=u'Location of config file.')
    parser.add_argument(
            u'-l', u'--log-level', metavar=u'LOG_LEVEL',
            dest='log_level', help=u'Log level.',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='WARNING',
            )
    parser.add_argument(
            u'command', choices=commands.keys(), default='lesson',
            help=u'Command to execute.', nargs='?')

    args = parser.parse_args(argv)

    log.set_log_level(args.log_level)

    if args.config_file is None:
        config = {}
    else:
        exec(args.config_file)
        args.config_file.close()
    config = ConfigManager(config)

    log.info(u'Config loaded.')

    commands[args.command](config, args)

    log.info(u'Program finished.')


if __name__ == '__main__':
    main()
