import multiprocessing
import threading
from confluent_kafka import Producer
import json

_requests_queue: multiprocessing.Queue = None

def proceed_to_deliver(id, details):
    # print(f"[debug] queueing for delivery event id: {id}, payload: {details}")
    details['authorized'] = True
    _requests_queue.put(details)


def producer_job(_, config, requests_queue: multiprocessing.Queue):
    # Create Producer instance
    producer = Producer(config)

    def delivery_callback(err, msg):
        if err:
            print('[error] Message failed delivery: {}'.format(err))
        # else:
        #     print("[debug]Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
        #         topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

    # Produce data by selecting random values from these lists.    

    while True:
        event_details = requests_queue.get()        
        topic = event_details['deliver_to']
        producer.produce(topic, json.dumps(event_details), event_details['id'],  
            callback=delivery_callback
        )
        producer.poll(10000)
        producer.flush()

def start_producer(args, config, requests_queue):
    global _requests_queue
    _requests_queue = requests_queue
    threading.Thread(target=lambda: producer_job(args, config, requests_queue)).start()
    
if __name__ == '__main__':
    start_producer(None, None, None)