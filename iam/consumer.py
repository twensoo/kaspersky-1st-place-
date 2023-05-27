# implements Kafka topic consumer functionality

import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from uuid import uuid4
from itertools import cycle
from producer import proceed_to_deliver

_users: dict = None

def get_user(user):
    role = "guest"
    if user in _users["engineer"]:
        role = "engineer"
    if user in _users["operator"]:
        role = "operator"
    if user in _users["observer"]:
        role = "observer"
    key = _users[role][user]
    return {'login': user, 'role': role, 'key': key}

def encrypt_decrypt(data: str, key: str):
    return ''.join(chr(ord(c)^ord(k)) for c,k in zip(data, cycle(key))) 

def handle_event(id: str, details: dict):    
    # print(f"[debug] handling event {id}, {details}")
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        login = details['user']
        del details['user']
        user = get_user(login)

        # attempt to decrypt payload with the requested user's key
        # it should produce valid json with necessary fields
        # if it fails, user (key) is wrong
        decrypted = encrypt_decrypt(details['data'], user['key'])
        data = json.loads(decrypted)
        del details['data']
        del user['key']
        # identification and authentication based on payload data which is encrypted with user's private key
        if login != data['login']:
            raise Exception('Access denied')
        
        details['id'] = uuid4().__str__()

        if details['operation'] == 'update_plc_software' and user['role'] == 'engineer':
            # add new digest in licenses db
            details['operation'] = 'new_update_digest'
            details['deliver_to'] = 'license_server'
            details['digest'] = data['digest']
            proceed_to_deliver(id, details)

            # notify update manager about new version
            del details['digest']
            details['id'] = uuid4().__str__()
            details['module_name'] = data['module_name']
            details['operation'] = 'launch_software_update'
            details['deliver_to'] = 'update_manager'
            proceed_to_deliver(id, details)

        elif details['operation'] == 'run_command' and user['role'] == 'operator':
            details['deliver_to'] = 'plc_control'
            details['command'] = data['command']
            proceed_to_deliver(id, details)
            
        elif details['operation'] == 'change_settings' and user['role'] == 'operator':
            details['deliver_to'] = 'plc_control'
            details['settings'] = data['settings']
            proceed_to_deliver(id, details)
            
        elif details['operation'] == 'hard_stop' and user['role'] == 'operator':
            details['deliver_to'] = 'cutoff'
            proceed_to_deliver(id, details)
            
        elif details['operation'] == 'check_user':
            # already checked by no except on JSONDecodeError
            auth = {
                'authorized': True,
                'user': user['login'],
                'role': user['role']
            }
            details['auth'] = auth
            details['operation'] = 'authorize_user'
            details['deliver_to'] = 'scada_out'
            proceed_to_deliver(id, details)
            
    except json.JSONDecodeError as je:
        print(f'error {je} {decrypted}') 
        details['id'] = uuid4().__str__()
        auth = {'authorized': False}
        details['auth'] = auth
        details['operation'] = 'authorize_user'
        details['deliver_to'] = 'scada_out'
        proceed_to_deliver(id, details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")

def consumer_job(args, config):
    # Create Consumer instance
    iam_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(iam_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            iam_consumer.assign(partitions)

    # Subscribe to topic
    topic = "iam"
    iam_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = iam_consumer.poll(1.0)
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
        iam_consumer.close()


def start_consumer(args, config, users):
    global _users
    _users = users
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None, None, None)