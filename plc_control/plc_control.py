#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from multiprocessing import Queue
from consumer import start_consumer
from producer import start_producer
from processor import start_processor

if __name__ == '__main__':
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
    config.update(config_parser['plc_control'])

    requests_queue = Queue()
    start_processor()
    start_consumer(args, config)
    start_producer(args, config, requests_queue)    

# import base64
# import hashlib
# import json
# import os
# import random
# import subprocess
# import time
# from urllib.request import urlopen
# import requests
# from flask import Flask, request, jsonify
# from uuid import uuid4
# import threading

# host_name = "0.0.0.0"
# port = 6064

# app = Flask(__name__)  # create an app instance

# # key = ''
# # timestamp = 0

# max_speed = 2900
# max_power = 19000
# max_temperature = 45
# min_speed = 333
# min_power = 1000
# min_temperature = 5

# CONTENT_HEADER = {"Content-Type": "application/json"}
# SCADA_SERVICE_ENDPOINT_URI = "http://scada:6069/service_message_from_plc"

# @app.route("/upload_update", methods=['POST'])
# def upload_update():
#     content = request.json
#     #global key, timestamp
#     try:
        
#         response = requests.post(
#                 "http://license_server:6067/check_license",
#                 headers=CONTENT_HEADER,
#             )
#         response = json.loads(response.content.decode('utf8'))
        
#         if response['status'] is True:

#         # if content['secret_key'] == key and abs(time.time() - timestamp) < 10:
#         #     del content['secret_key']
        
#             with open("/storage/version_plc.json", "w") as f:
#                 json.dump(content, f)
            
#             data = {
#                "device": 'plc',
#                "value": 'Updates uploaded!'
#             }
#             requests.post(
#                 SCADA_SERVICE_ENDPOINT_URI,
#                 data=json.dumps(data),
#                 headers=CONTENT_HEADER,
#             )
#         else:
#             print("Ошибка лицензирования!")
#     except Exception as _:
#         error_message = f"malformed request {request.data}"
#         return error_message, 400
#     return jsonify({"operation": "stopped"})


# @app.route("/upload_settings", methods=['POST'])
# def upload_settings():
#     content = request.json
#     global max_power, max_speed, max_temperature, min_temperature, min_power, min_speed
#     try:
#         with open("/storage/settings_plc.json", "w") as f:
#             json.dump(content, f)
#         max_power = content['max_power']
#         max_speed = content['max_speed']
#         max_temperature = content['max_temperature']
#         min_power = content['min_power']
#         min_speed = content['min_speed']
#         min_temperature = content['min_temperature']
#         data = {
#                "device": 'plc',
#                "value": 'Settings uploaded!'
#            }
#         requests.post(
#                 SCADA_SERVICE_ENDPOINT_URI,
#                 data=json.dumps(data),
#                 headers=CONTENT_HEADER,
#         )
#     except Exception as _:
#         error_message = f"malformed request {request.data}"
#         return error_message, 400
#     return jsonify({"operation": "stopped"})


# @app.route("/command", methods=['POST'])
# def command():
#     global max_power, max_speed, max_temperature, min_temperature, min_power, min_speed
#     content = request.json
#     try:
#         if content['device'] == 'plc':
#             if content['operation'] == 'reboot':
#                 with open("/storage/settings_plc.json", "r") as f:
#                     data = json.load(f)
#                     max_power = data['max_power']
#                     max_speed = data['max_speed']
#                     max_temperature = data['max_temperature']
#                     min_power = data['min_power']
#                     min_speed = data['min_speed']
#                     min_temperature = data['min_temperature']
#                 print("Перезагружено")
#         else:
#             print('Команда отправлена на датчик')
#             requests.post(
#                     "http://sensors:6068/" + content['operation'],
#                     data=json.dumps(content),
#                     headers=CONTENT_HEADER,
#             )
#     except Exception as _:
#         print("[error] некорректная команда! ")
#         return "Bad command detected", 400
#     return jsonify({"operation": "start requested", "status": True})


# #получение данных на вход
# @app.route("/data_in", methods=['POST'])
# def data():
#     content = request.json
#     delivery_required = False
#     msg = ''
    
#     try:
#         requests.post(
#                 "http://scada:6069/data_message_from_plc",
#                 data=json.dumps(content),
#                 headers=CONTENT_HEADER,
#         )
#         if content['device'] == 'temperature_device':
#            if content['value'] > max_temperature or content['value'] < min_temperature:
#                msg = "[Alarm] значения температуры выходят за установленные рамки!"
#                delivery_required = True
#         if content['device'] == 'speed_device':
#            if content['value'] > max_speed or content['value'] < min_speed:
#                msg = "[Alarm] значения скорости выходят за установленные рамки!"
#                delivery_required = True
#         if content['device'] == 'power_device':
#            if content['value'] > max_power or content['value'] < min_power:
#                msg = "[Alarm] значения мощности выходят за установленные рамки!"
#                delivery_required = True
#         if delivery_required:
#            data = {
#                "device": content['device'],
#                "value": msg
#            }
#            requests.post(
#                 SCADA_SERVICE_ENDPOINT_URI,
#                 data=json.dumps(data),
#                 headers=CONTENT_HEADER,
#             )
#     except Exception as _:
#         error_message = f"malformed request {request.data}"
#         return error_message, 400
#     return jsonify({"operation": "data_in", "status": True})

# # @app.route("/key", methods=['POST'])
# # def key():
# #     content = request.json
# #     global key, timestamp
# #     try:
# #         key = content['key']
# #         timestamp = time.time()
# #         print("[KEY] авторизован ключ")
# #     except Exception as _:
# #         error_message = f"malformed request {request.data}"
# #         return error_message, 400
# #     return jsonify({"operation": "key_in ", "status": True})


# if __name__ == "__main__":
#     app.run(port=port, host=host_name)
    
