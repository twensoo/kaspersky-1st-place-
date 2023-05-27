from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from itertools import cycle
from uuid import uuid4
import pytest
import json

consumer: KafkaConsumer = None
producer: KafkaProducer = None
operator_user: dict = None
observer_user: dict = None
engineer_user: dict = None

@pytest.fixture(autouse=True)
def iam_env_preparing():
    global consumer, producer, operator_user, observer_user, engineer_user

    operator_user = {
        'user': 'Vasa',
        'key': '123456'
    }
    observer_user = {
        'user': 'observer2',
        'key': '54321'
    }
    engineer_user = {
        'user': 'engineer1',
        'key': 'password'
    }

    consumer = KafkaConsumer(
                         group_id='tester',
                         bootstrap_servers=['su-broker:9192'],
                         auto_offset_reset="latest",
                         enable_auto_commit=False,
                         value_deserializer=lambda m: json.loads(m.decode('ascii')))
    producer = KafkaProducer(bootstrap_servers=['su-broker:9192'])

def _encrypt_decrypt(data: str, key: str):
    return ''.join(chr(ord(c)^ord(k)) for c,k in zip(data, cycle(key))) 

def test_update_plc_software():
    req_id = uuid4().__str__()

    login = engineer_user['user']
    key = engineer_user['key']

    data = {
        'digest': uuid4().__str__(),
        'module_name': 'plc_control',
        'login': login
    }

    _data = _encrypt_decrypt(json.dumps(data), key)

    event_details = {
        'source': 'scada_in',
        'deliver_to': 'iam',
        'operation': 'update_plc_software',
        'user': login,
        'data': _data,
        'id': req_id
    }

    tp = TopicPartition('license_server', 0)
    consumer.assign([tp])

    producer.send('monitor', key=event_details['id'].encode(), value=json.dumps(event_details).encode())
    consumer.poll()
    consumer.seek_to_end()

    partition = list(consumer.assignment())[0]
    end_offset = consumer.end_offsets([partition])
    consumer.seek(partition,max(0, list(end_offset.values())[0]-2))

    for message in consumer:
        if message.value['source'] == 'iam':
            assert  message.value['operation'] == 'new_update_digest'
            break

def test_change_settings():
    req_id = uuid4().__str__()

    login = operator_user['user']
    key = operator_user['key']

    data = {
        'settings': {
        'min_power': 100,
        'max_power': 100000
        },
        'login': login
    }

    _data = _encrypt_decrypt(json.dumps(data), key)

    event_details = {
        'source': 'scada_in',
        'deliver_to': 'iam',
        'operation': 'change_settings',
        'user': login,
        'data': _data,
        'id': req_id
    }

    tp = TopicPartition('plc_control', 0)
    consumer.assign([tp])

    producer.send('monitor', key=event_details['id'].encode(), value=json.dumps(event_details).encode())
    consumer.poll()
    consumer.seek_to_end()

    partition = list(consumer.assignment())[0]
    end_offset = consumer.end_offsets([partition])
    consumer.seek(partition,max(0, list(end_offset.values())[0]-2))

    for message in consumer:
        if message.value['source'] == 'iam':
            assert  message.value['operation'] == 'change_settings'
            break