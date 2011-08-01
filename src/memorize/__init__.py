#!/usr/bin/python


""" **Memorize** is a program, which purpose is to help memorize
foreign language words.
"""


import sys
import argparse

from memorize.log import Logger
from memorize.config import ConfigManager
from memorize.parsers import ParsersManager


log = Logger('memorize', root=True)


def sync(config, args):
    """ Synchronizes ZODB with XML.
    """

    log.info(u'Starting sinchronization.')

    log.info(u'Loaded XML parsers:')
    for i, (tag, parser) in enumerate(config.xml_parsers.items()):
        log.info(u'parser{0:03}: (tag=\"{1}\", parser={2})',
            i, tag, parser)

    manager = ParsersManager(config)
    for file in manager.collect():
        manager.parse_file(file)


def main(argv=sys.argv[1:]):
    """ Main entry point.
    """

    commands = {
            'sync': sync,
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
            u'command', choices=commands.keys(),
            help=u'Command to execute.')

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
