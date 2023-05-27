# implements Kafka topic consumer functionality

import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from processor import update_settings, update_sensor_readings, run_command
from producer import proceed_to_deliver

def handle_event(id: str, details: dict):    
    # print(f"[debug] handling event {id}, {details}")
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        # TODO: implement handlers
        if details['operation'] == 'push_speed_value':
            speed = details['speed']
            update_sensor_readings({'speed': speed})
            details['deliver_to'] = 'scada_out'
            proceed_to_deliver(id, details)
            
        elif details['operation'] == 'push_temperature_value':
            temperature = details['temperature']
            update_sensor_readings({'temperature': temperature})
            
        elif details['operation'] == 'push_power_value':
            power = details['power']
            update_sensor_readings({'power': power})
            
        elif details['operation'] == 'run_command':
            command = details['command']
            run_command(command)
            
        elif details['operation'] == 'change_settings':
            settings = details['settings']
            update_settings(settings)

    except Exception as e:
        print(f"[error] failed to handle request: {e}")

def consumer_job(args, config):
    # Create Consumer instance
    plc_control_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(plc_control_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            plc_control_consumer.assign(partitions)

    # Subscribe to topic
    topic = "plc_control"
    plc_control_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = plc_control_consumer.poll(1.0)
            if msg is None:
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                try:
                    id = msg.key().decode('utf-8')
                    details_str = msg.value().decode('utf-8')
                    # TODO: decrypt msg
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
        plc_control_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)