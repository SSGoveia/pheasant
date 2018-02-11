"""Decorators are provided to control run-export process."""
import logging
import os
from functools import wraps

from .config import config

logger = logging.getLogger('pheasant')


def pheasant_options(cell) -> list:
    """Get pheasant options from cell's metadata."""
    if 'pheasant' in cell.metadata:
        return cell.metadata['pheasant']['options']
    else:
        return []


def abort(func):
    run = True

    @wraps(func)
    def decorator(cell, *args, **kwargs):
        nonlocal run

        if config.setdefault('run_counter', 0) == 0:
            run = True

        if run:
            markdown = func(cell, *args, **kwargs)
        else:
            markdown = '**Aborted**'

        if 'abort' in pheasant_options(cell):
            run = False

        return markdown

    return decorator


def memoize(func):
    """
    Store the run-export results in cache.

    If source of cell is changed, the following
    markdown results are dropped and will be rerun after.
    """
    cache = {}

    @wraps(func)
    def decorator(cell, *args, **kwargs):
        from ..converters import get_source_file
        source_file = get_source_file()
        counter = config.setdefault('run_counter', 0)
        config['run_counter'] += 1

        if 'clear' in pheasant_options(cell):
            cache[source_file] = []

        source_markdown = cache.get(source_file, [])
        if len(source_markdown) >= counter + 1:
            source, markdown = source_markdown[counter]
            if cell.source == source:
                return markdown

        logger.debug(
            f'Running cell: {os.path.basename(source_file)}:{counter}')
        markdown = func(cell, *args, **kwargs)

        cache[source_file] = (source_markdown[:counter] +
                              [(cell.source, markdown)])
        return markdown

    return decorator