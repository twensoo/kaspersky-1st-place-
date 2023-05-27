from multiprocessing import Queue
from flask import Flask, request, jsonify
import requests
from uuid import uuid4
import os
import threading
import json
from producer import proceed_to_deliver

host_name = "0.0.0.0"
port = os.getenv("SCADA_OUTPUT_API_PORT", default=6070)
CONTENT_HEADER = {"Content-Type": "application/json"}

app = Flask(__name__)             # create an app instance
auth_responses_queue: Queue = None

observers = []
operators = []
device_event: threading.Event = None

sensor_readings = {
    'speed': 0,
    'power': 0,
    'temperature': 0
}

def add_auth_response(auth_response):
    global auth_responses_queue
    auth_responses_queue.put(auth_response)

def update_sensor_readings(readings: dict):
    global sensor_readings
    if 'speed' in readings:
        sensor_readings["speed"] = readings.get('speed')
    if 'power' in readings:
        sensor_readings["power"] = readings.get('power')
    if 'temperature' in readings:
        sensor_readings["temperature"] = readings.get('temperature')
    device_event.set()

def feed_job():
    global device_event
    while True:
        device_event.wait()

        for subscriber in (observers + operators):
            requests.post(
             subscriber,
             data=json.dumps(sensor_readings),
             headers=CONTENT_HEADER)

        device_event.clear()

def report_alert(description):
    for subscriber in operators:
        requests.post(
             subscriber,
             data=json.dumps({'alert': description}),
             headers=CONTENT_HEADER)

def add_subscriber(auth, address):
    try:
        if auth['authorized'] == False:
            return
        if 'observer' == auth['role']:
            observers.append(address)
        elif 'operator' == auth['role']:
            operators.append(address)
    except:
        print(f'malformed auth response {auth}')

@app.route("/subscribe", methods=['POST'])
def subscribe():
    req_id = uuid4().__str__()
    try:
        content = request.json
        details = {
            "id": req_id,
            "operation": 'check_user',
            "user": content['user'],
            "data": content['data'],
            "deliver_to": "iam"
        }
        proceed_to_deliver(req_id, details)

        auth = auth_responses_queue.get()
        add_subscriber(auth, content['address'])
    except:
        error_message = f"malformed request {request.data}"
        print(error_message)
        return error_message, 403


def start_rest():
    global auth_responses_queue, device_event 
    auth_responses_queue = Queue()
    device_event = threading.Event()
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()
    threading.Thread(target=lambda: feed_job()).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()