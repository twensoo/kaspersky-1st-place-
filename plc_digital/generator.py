import threading
import time
from multiprocessing import Queue
from uuid import uuid4
from producer import proceed_to_deliver

CLEAR_INTERVAL_SEC = 60.1
DELIVERY_INTERVAL_SEC = 5

impulses: Queue = None

def add_impulse():
    global impulses
    impulses.put(1)

def generator_job():
    global impulses
    while True:
        time.sleep(DELIVERY_INTERVAL_SEC)
        speed = impulses.qsize() * 500
        req_id = uuid4().__str__()
        details = {
            'deliver_to': 'plc_control',
            'operation': 'push_speed_value',
            'speed': speed,
            'id': req_id
        }
        proceed_to_deliver(req_id, details)


def impulse_job():
    global impulses
    while True:
        time.sleep(CLEAR_INTERVAL_SEC)
        try:
            impulses.get_nowait()
        except:
            pass

def start_generator():
    global impulses
    impulses = Queue()
    threading.Thread(target=lambda: impulse_job()).start()
    threading.Thread(target=lambda: generator_job()).start()

if __name__ == '__main__':
    start_generator(None)