"""Simple log functions
"""
import sys
import traceback

import config


def debug(msg):
    if config.debug:
        error(msg)


def error(msg):
    sys.stderr.write(str(msg))
    sys.stderr.write("\n")


def info(msg):
    print(msg)


def log_traceback(ex):
    _, _, ex_traceback = sys.exc_info()
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [line.rstrip('\n') for line in
                traceback.format_exception(ex.__class__, ex, ex_traceback)]
    error(tb_lines)
