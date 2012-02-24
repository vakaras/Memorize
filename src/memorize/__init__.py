#!/usr/bin/python


""" **Memorize** is a program, which purpose is to help memorize
foreign language words.
"""


import sys
import argparse
import random

import transaction

from memorize.log import Logger
from memorize.config import ConfigManager
from memorize.parsers import ParsersManager
from memorize.manipulators import ManipulatorsManager


log = Logger('memorize', root=True)


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
        u'Qustions for today: {0}.\n'.format(len(questions))
        ).encode('utf-8'))

    separator = '-' * 60 + '\n'
    for question in questions:
        sys.stdout.write(separator)
        question.show(sys.stdout)
        answer = raw_input(u'Answer: ').decode('utf-8')
        question.parse_answer(answer, sys.stdout)
        transaction.commit()
        log.info(u'Changes committed.')

    log.info(u'Lesson finished.')


def get_free_id(config, args):
    """ Prints smallest unused object id.
    """

    print config.tag_tree._counter


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
