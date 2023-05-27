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
    config.update(config_parser['scada_in'])

    requests_queue = Queue()
 
    start_rest()    
    start_producer(args, config, requests_queue)

# import json

# import requests
# from flask import Flask, request, jsonify

# CONTENT_HEADER = {"Content-Type": "application/json"}

# host_name = "0.0.0.0"
# port = 6069

# app = Flask(__name__)             # create an app instance

# observers_list = []
# operators_list = []

# def logger(role, login, password):
#     users = open('/storage/users.json', 'r')
#     data = json.load(users)
#     users.close()

#     if (login in data[role]) and (data[role][login] == password):
#         return True
#     else: 
#         return False
        


# @app.route("/log_in", methods=['POST'])
# def log_in():
#     global observers_list, operators_list
#     try:
#         content = request.json
        
#         if logger('observer', content['login'], content['password']):
#             temp = [content['login'], content['url']]
#             observers_list.append(temp)
#             print(f"[LOGIN] авторизован пользователь: {content['login']}")

#         elif logger('operator', content['login'], content['password']):
#             temp = [content['login'], content['url']]
#             operators_list.append(temp)
#             print(f"[LOGIN] авторизован пользователь: {content['login']}")

        
#     except Exception as e:
#         print(f"exception raised: {e}")
#         return "BAD REQUEST", 400
#     return jsonify({"status": True})

# @app.route("/log_out", methods=['POST'])
# def log_out():
#     global operators_list, observers_list
#     try:
#         content = request.json
#         for i in operators_list:
#             if i[0] == content['login']:
#                 operators_list.remove(i)
#                 print(f"[LOGIN] пользователь вышел из системы: {content['login']}")
#         for i in observers_list:
#             if i[0] == content['login']:
#                 observers_list.remove(i)
#                 print(f"[LOGIN] пользователь вышел из системы: {content['login']}")
#     except Exception as e:
#         print(f"exception raised: {e}")
#         return "BAD REQUEST", 400
#     return jsonify({"status": True})

# @app.route("/upload_settings", methods=['POST'])
# def upload_settings():
#     try:
#         content = request.json
#         if logger('operator', content['login'], content['password']):
#             del content['login']
#             del content['password']
#             with open("/storage/settings_scada.json", "w") as f:
#                 json.dump(content, f)

#             requests.post(
#             "http://plc:6064/upload_settings",
#             data=json.dumps(content),
#             headers=CONTENT_HEADER,
#             )
#             print("Настройки обновлены")
#     except Exception as e:
#         print(f"exception raised: {e}")
#         return "BAD CREDENTIALS", 401
#     return jsonify({"operation": "upload_settings", "status": True})

# @app.route("/upload_update", methods=['POST'])
# def upload_update():
#     try:
#         content = request.json
#         headers = request.headers
#         # users = open('/storage/users.json', 'r')
#         # data = json.load(users)
#         # users.close()
        
#         if logger('engineer', headers['login'], headers['password']):
#         #if headers['login'] in data['engineer'] and (data['engineer'][headers['login']][0] == headers['password']): 
#             with open("/storage/version_scada.json", "w") as f:
#                 json.dump(content, f)
            
#             #content['secret_key'] = data['engineer'][headers['login']][1]
#             requests.post(
#             "http://plc:6064/upload_update",
#             data=json.dumps(content),
#             headers=CONTENT_HEADER,
#             )
#             print("Обновление отправлено на ПЛК")

#     except Exception as e:
#         print(f"exception raised: {e}")
#         return "BAD CREDENTIALS", 401
#     return jsonify({"operation": "upload_update", "status": True})

# @app.route("/command_to_plc", methods=['POST'])
# def command_to_plc():
#     try:
#         content = request.json
#         if logger('operator', content['login'], content['password']):
#             del content['login']
#             del content['password']
#             requests.post(
#                 "http://plc:6064/command",
#                 data=json.dumps(content),
#                 headers=CONTENT_HEADER,
#                 )
#             print("Команда отправлена на контроллер")
#     except Exception as e:
#         print(f"exception raised: {e}")
#         return "BAD CREDENTIALS", 401
#     return jsonify({"operation": "command_to_plc", "status": True})


# @app.route("/service_message_from_plc", methods=['POST'])
# def service_msg():
#     global operators_list
#     try:
#         content = request.json
#         for i in operators_list:
#             requests.post(
#                 i[1],
#                 data=json.dumps(content),
#                 headers=CONTENT_HEADER,
#             )
#     except Exception as e:
#         print(f"exception raised: {e}")
#         return "BAD REQUEST", 400
#     return jsonify({"operation": "service_msg", "status": True})


# @app.route("/data_message_from_plc", methods=['POST'])
# def data_msg():
#     global operators_list, observers_list
#     try:
#         content = request.json
#         for i in operators_list:
#             requests.post(
#                 i[1],
#                 data=json.dumps(content),
#                 headers=CONTENT_HEADER,
#             )
#         for i in observers_list:
#             requests.post(
#                 i[1],
#                 data=json.dumps(content),
#                 headers=CONTENT_HEADER,
#             )
            
#     except Exception as e:
#         print(f"exception raised: {e}")
#         return "BAD REQUEST", 400
#     return jsonify({"operation": "data_msg", "status": True})

# if __name__ == "__main__":        
#     app.run(port = port, host=host_name)