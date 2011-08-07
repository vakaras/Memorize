===========================
The work flow of *Memorize*
===========================

Main work flow
==============

#.  Parse command line arguments.
#.  Initialize logging.
#.  Load configuration.

    +   Check correctness.

#.  Connect to ZODB.

    +   *Optional:* create file storage.

#.  Load plugins.
#.  Execute *action*. Where, *action* is one of:

    +   :ref:`lesson <lesson_workflow>` – take a lesson;
    +   :ref:`sync <sync_workflow>` – synchronize ZODB with XML storage.

.. _sync_workflow:

*sync* work flow
================

#.  Collect XML files.
#.  Parse XML files.
#.  Finalize parsing.

    +   Told to each parser, that reading files is finished.

#.  Commit or abort changes.

.. _lesson_workflow:

*lesson* work flow
==================

#.  Create a lesson.

    .. note::
        Database in this state is just read only. Manipulators shouldn't
        write into a database, when creating questions.

    #.  Initialize manipulators.
    #.  Collect questions from manipulators.
    #.  Random sort questions.

#.  Give a lesson.

    For each question:

    #.  Show question.
    #.  Parse answer.
    #.  Update information holders state.
    #.  Commit changes.
