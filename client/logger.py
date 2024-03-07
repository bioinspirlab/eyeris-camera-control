# -*- coding: utf-8 -*-
"""
logger.py -- wrapper around python logging to support logging to file and screen at the same time
Copyright 2020  Monterey Bay Aquarium Research Institute
Distributed under MIT license. See license.txt for more information.

"""

import os
import time
import logging

def get_logger(filepath,file_level=logging.DEBUG, console_level=logging.WARN,logger_name=''):
    """Get a logger object initialized with console and file output

    Parameters:
    -----------
    filepath : str
        The absolue path to the file for the FileHandler
    log_level : {'DEBUG', 'INFO', 'WARNING','ERROR','CRITICAL'}
        The log level for the logger,
    logger_name : str, optional
        A string prepended to each log message

    Returns:
    --------
    lgr: logger
        An initialized logger object

    """
    # create logger
    lgr = logging.getLogger(logger_name)
    lgr.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(console_level)

    fh = logging.FileHandler(filepath)
    fh.setLevel(file_level)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add ch to lgr
    lgr.addHandler(ch)
    lgr.addHandler(fh)

    return lgr

def get_file_logger(filepath,file_level=logging.DEBUG,logger_name=''):
    """Get a logger object initialized with console and file output

        Parameters:
        -----------
        filepath : str
            The absolue path to the file for the FileHandler
        log_level : {'DEBUG', 'INFO', 'WARNING','ERROR','CRITICAL'}
            The log level for the logger,
        logger_name : str, optional
            A string prepended to each log message

        Returns:
        --------
        lgr: logger
            An initialized logger object

        """
    # create logger
    lgr = logging.getLogger(logger_name)
    lgr.setLevel(logging.DEBUG)

    fh = logging.FileHandler(filepath)
    fh.setLevel(file_level)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    fh.setFormatter(formatter)

    # add ch to lgr
    lgr.addHandler(fh)

    return lgr
