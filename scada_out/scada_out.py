#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from api import start_rest
from producer import start_producer
from multiprocessing import Queue

if __name__ == "__main__":
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'))
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()
    # Parse the configuration.
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md

    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser['default'])
    config.update(config_parser['scada_out'])

    requests_queue = Queue()
    start_rest()    
    start_producer(args, config, requests_queue)