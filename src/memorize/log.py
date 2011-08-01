#!/usr/bin/python


""" Module, which setup logging and provide some shortcuts.
"""


import logging


class Logger(object):
    """ Objects, which wraps logging to provide str.format for message
    formating.
    """

    def __init__(self, name, level=None, root=False):

        self.name = name
        self._logger = None
        self.root = root                # Root logger?

        if level is not None:
            self.set_log_level(level)

    @property
    def logger(self):
        """ Makes logger lazy -- it is created only, when really needed.
        """

        if self._logger is None:

            logger = logging.getLogger(self.name)

            if self.root:

                formatter = logging.Formatter(
                        u'%(levelname)s %(name)s: %(message)s')

                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(formatter)

                logger.addHandler(console_handler)

            self._logger = logger

        return self._logger

    def set_log_level(self, level):
        """ Change log level.

        :param level: One of DEBUG, INFO, WARNING, ERROR, CRITICAL
        """

        self.logger.setLevel(getattr(logging, level))

    def debug(self, message, *args, **kwargs):
        """ Log DEBUG level message.
        """

        self.logger.debug(message.format(*args, **kwargs))

    def info(self, message, *args, **kwargs):
        """ Log INFO level message.
        """

        self.logger.info(message.format(*args, **kwargs))

    def warn(self, message, *args, **kwargs):
        """ Log WARNING level message.
        """

        self.logger.warn(message.format(*args, **kwargs))
