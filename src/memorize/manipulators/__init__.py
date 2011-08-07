#!/usr/bin/python


"""
Mount point for all manipulators.
"""


from memorize.plugins import MountPoint


class ManipulatorPlugin(object):
    """ Base class for any plugin, which implements manipulators.

    Plugin manager will look for these methods:

    +   ``__init__(plugin_manager: PluginManager)``;
    +   ``get_questions()`` -- should return list of questions, where
        question is an object, which has methods:

        +   ``show(fp: file)`` -- prints question to given file object;
        +   ``parse_answer(answer: unicode, fp: file)`` -- parses
            answer and prints response about the answer to given file.

        .. note::
            After calling ``parse_answer`` changes are automatically
            committed to database, so ``parse_answer`` shouldn't make
            any partial changes to data.
    """

    __metaclass__ = MountPoint

    def __init__(self, plugin_manager):
        pass


class ManipulatorsManager(object):
    """ :py:class:`ManipulatorsManager` initializes manipulators, collects
    and shows questions from them.
    """

    def __init__(self, config):

        self.config = config
        self.manipulators = []
        self.manipulators_classes = config.manipulators
        self.tag_tree = config.tag_tree

    def init_manipulators(self):
        """ Initializes manipulators.
        """

        for manipulator_class in self.manipulators_classes:
            self.manipulators.append(manipulator_class(self))

    def collect_questions(self):
        """ Returns list of questions collected from manipulators.
        """

        questions = []
        for manipulator in self.manipulators:
            questions.extend(manipulator.get_questions())

        return questions
