#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import os
import time
import datetime
import logging
import signal

if sys.version_info[0] < 3:
    raise Exception('Please use Python 3!')

"""Program to monitor directories and files for a magic keyphrase taken from a
   command line argument. If the magic phrase is found, a new message will be
   logged with the file and line number the text was found."""

__author__ = """chewh115, sighandler and main taken from assessment overview,
                watched and coded along with Mike A's demo walk through
                Formatter adapted from
                https://www.programcreek.com/python/example/192/logging.Formatter"""

# Globals
exit_flag = False

# Sets up logging to console
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(process)d - %(message)s')
stream = logging.StreamHandler()
stream.setFormatter(formatter)
logger.addHandler(stream)


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here
    as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if
    the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name (the python3 way)
    logger.warning('Received ' + signal.Signals(sig_num).name)

    global exit_flag
    exit_flag = True


def watch_dir(directory, magic, ext, interval):
    """Watches given directory for file changes"""
    files_dict = {}
    while not exit_flag:
        for filename in os.listdir(directory):
            if filename.endswith(ext) and filename not in files_dict:
                logger.info(f'Found new file {filename} to monitor!')
                files_dict[filename] = 0
        for filename in list(files_dict):
            if filename not in os.listdir(directory):
                files_dict.pop(filename)
                logger.info(f'{filename} has been removed from {directory}')
            else:
                full_path = os.path.join(directory, filename)
                files_dict[filename] = scan_file(
                    full_path, magic, files_dict[filename])
        time.sleep(interval)


def scan_file(filename, magic, start_line):
    """Scans a given file to see if it contains the magic word, starting at
       the last line scanned"""
    with open(filename, 'r') as f:
        scanning_line = 0
        for scanning_line, line in enumerate(f):
            if scanning_line >= start_line:
                if magic in line:
                    logger.info(
                        f'Found {magic} in {scanning_line+1} of {filename}!')
        return scanning_line + 1


def main():
    # Hook these two signals from the OS ..
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS
    # sends either of these to my process.

    start_time = datetime.datetime.now()
    logger.info(
        '\n'
        '----------------------------------------\n'
        f'Starting {__file__}\n'
        f'Process ID: {os.getpid()}\n'
        f'Started at: {start_time}\n'
        '----------------------------------------\n'
    )

    parser = argparse.ArgumentParser(
        description="Accepts directory to monitor & magic word to search for")
    parser.add_argument('--ext',
                        help='Extension of files to search through',
                        default='.txt')
    parser.add_argument('--int', type=float,
                        help='Interval to search through files',
                        default=1.0)
    parser.add_argument('dir', help='Directory to watch')
    parser.add_argument('magic', help='Magic key to search files for')
    args = parser.parse_args()

    logger.info(
        f'Searching for {args.magic} in {args.dir} for {args.ext}')

    while not exit_flag:
        try:
            watch_dir(args.dir, args.magic, args.ext, args.int)
            logger.debug(f'Watching directory {args.dir}')
            pass
        except FileNotFoundError:
            logger.warning(f'{args.dir} doesn\'t exist!')
        except Exception as e:
            logger.error(f'We have an unhandled error {e}!')
        time.sleep(3.0)

    uptime = datetime.datetime.now() - start_time

    logger.info(
        '\n'
        '----------------------------------------\n'
        f'Stopped {__file__}\n'
        f'Total running time: {uptime}\n'
        '----------------------------------------\n')

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start.


if __name__ == '__main__':
    main()
