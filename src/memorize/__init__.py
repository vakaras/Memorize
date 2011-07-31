#!/usr/bin/python


""" **Memorize** is a program, which purpose is to help memorize
foreign language words.
"""


import sys
import argparse

from memorize.config import ConfigManager

def main(argv=sys.argv[1:]):
    """ Main entry point.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
            u'-c', u'--config', metavar=u'CONFIG_FILE', type=file,
            dest=u'config_file', help=u'Location of config file.')

    args = parser.parse_args(argv)

    if args.config_file is None:
        config = {}
    else:
        exec(args.config_file)
        args.config_file.close()
    config = ConfigManager(config)

    config.connect()


if __name__ == '__main__':
    main()
