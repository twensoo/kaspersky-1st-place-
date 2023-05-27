import threading
import time
from uuid import uuid4
from producer import proceed_to_deliver

DELIVERY_INTERVAL_SEC = 10
STANDARD_SPEED = 3000
STANDARD_INTERVAL = 10
device_event: threading.Event = None

def shutdown():
    global device_event
    device_event.clear()

def change_speed(target_speed):
    global DELIVERY_INTERVAL_SEC
    DELIVERY_INTERVAL_SEC = STANDARD_SPEED * STANDARD_INTERVAL / target_speed

def generator_job():
    global device_event
    while device_event.is_set():
        time.sleep(DELIVERY_INTERVAL_SEC)
        req_id = uuid4().__str__()
        details = {
            'deliver_to': 'plc_digital',
            'operation': 'push_speed_impulse',
            'id': req_id
        }
        proceed_to_deliver(req_id, details)

def start_generator():
    global device_event
    device_event = threading.Event()
    device_event.set()
    threading.Thread(target=lambda: generator_job()).start()

if __name__ == '__main__':
    start_generator()