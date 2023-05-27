#!/usr/bin/env python

import os
from flask import Flask, make_response, send_file, abort, request, jsonify
from werkzeug.utils import secure_filename
from hashlib import sha256

host_name = "0.0.0.0"
port = os.getenv("TESTS_SERVER_PORT", default=6064)

app = Flask(__name__)

if __name__ == "__main__":        # on running python app.py
    app.run(port=port, host=host_name)

# from confluent_kafka import Producer
# from argparse import ArgumentParser, FileType
# from configparser import ConfigParser
# from uuid import uuid4
# from multiprocessing import Queue
# from producer import proceed_to_deliver, start_producer
# import os
# import requests
# import json

# ########## downloader ##########

# def test_downloader():
#     print('[info] testing downloader')
#     req_id = uuid4().__str__()
#     event_details = {
#         'module_name': 'plc_control',
#         'source': 'test',
#         'deliver_to': 'downloader',
#         'operation': 'request_download',
#         'id': req_id
#     }
#     event_details['source'] = 'iam'   
#     proceed_to_deliver(req_id, event_details)


# def test_all():
#     test_updates_server()
#     test_downloader()
#     test_scada_in()

# if __name__ == '__main__':
#     parser = ArgumentParser()
#     parser.add_argument('config_file', type=FileType('r'))
#     parser.add_argument('--reset', action='store_true')
#     args = parser.parse_args()
#     # Parse the configuration.
#     # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md

#     config_parser = ConfigParser()
#     config_parser.read_file(args.config_file)
#     config = dict(config_parser['default'])
#     config.update(config_parser['tester'])

#     requests_queue = Queue()
#     start_producer(args, config, requests_queue)
#     test_all()