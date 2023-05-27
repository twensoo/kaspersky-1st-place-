# implements Kafka topic consumer functionality

import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
from api import update_sensor_readings, add_auth_response, report_alert
import json


def handle_event(id: str, details: dict):
    # print(f"[debug] handling event {id}, {details}")
    print(
        f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        if details['operation'] == 'authorize_user':
            auth_resp = details['auth']
            add_auth_response(auth_resp)
            
        elif details['operation'] == 'push_speed_value':
            speed = details['speed']
            update_sensor_readings({'speed': speed})

        elif details['operation'] == 'push_temperature_value':
            temperature = details['temperature']
            update_sensor_readings({'temperature': temperature})

        elif details['operation'] == 'push_power_value':
            power = details['power']
            update_sensor_readings({'power': power})

        elif details['operation'] == 'send_alert':
            description = details['description']
            report_alert(description)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")


def consumer_job(args, config):
    # Create Consumer instance
    scada_out_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(scada_out_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            scada_out_consumer.assign(partitions)

    # Subscribe to topic
    topic = "scada_out"
    scada_out_consumer.subscribe([topic], on_assign=reset_offset)
    
    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = scada_out_consumer.poll(1.0)
            
            if msg is None:
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                # Extract the (optional) key and value, and print.
                try:
                    id = msg.key().decode('utf-8')
                    details_str = msg.value().decode('utf-8')
                    # print("[debug] consumed event from topic {topic}: key = {key:12} value = {value:12}".format(
                        # topic=msg.topic(), key=id, value=details_str))
                    handle_event(id, json.loads(details_str))
                except Exception as e:
                    print(
                        f"Malformed event received from topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        scada_out_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)