"""Simple log functions
"""
import sys
import traceback

import config


def debug(msg):
    """Display messages to stderr only when L{config.debug} is True

    @param msg: The message to write to stderr. It can be anything that
                can be turned into a string.
    """
    if config.debug:
        error(msg)


def error(msg):
    """Write a message to stderr

    @param msg: The message to write to stderr. It can be anything that
                can be turned into a string.
    """
    sys.stderr.write(str(msg))
    sys.stderr.write("\n")


def info(msg):
    """Write a message to stdout

    @param msg: The message to write to stdout. It can be anything that
                can be turned into a string.
    """
    print(msg)


def log_traceback(ex):
    """Log an exception and traceback without raising the exception.

    @param ex: The exception to log.
    @type ex: L{Exception}
    """
    error(ex)
    _, _, ex_traceback = sys.exc_info()
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [line.rstrip('\n') for line in
                traceback.format_exception(ex.__class__, ex, ex_traceback)]
    error(tb_lines)
