# implements Kafka topic consumer functionality


import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from api import add_digest

def handle_event(id: str, details: dict):
    # print(f"[debug] handling event {id}, {details}")
    print(
        f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    if details['operation'] == 'new_update_digest':
        digest = details['digest']
        add_digest(digest)

def consumer_job(args, config, events_queue=None):

    global _events_queue
    _events_queue = events_queue

    # Create Consumer instance
    license_server_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.

    def reset_offset(consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            consumer.assign(partitions)

    # Subscribe to topic
    topic = "license_server"
    license_server_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = license_server_consumer.poll(1.0)
            if msg is None:
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                try:
                    event_id = msg.key().decode('utf-8')
                    details = json.loads(msg.value().decode('utf-8'))
                    handle_event(event_id, details)
                except Exception as e:
                    print(
                        f"[error] malformed event received from topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        license_server_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(
        args, config)).start()
