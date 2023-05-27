from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from uuid import uuid4
import pytest
import json

consumer: KafkaConsumer = None
producer: KafkaProducer = None

@pytest.fixture(autouse=True)
def update_manager_env_preparing():
    global consumer, producer
    consumer = KafkaConsumer(
                         group_id='tester',
                         bootstrap_servers=['su-broker:9192'],
                         auto_offset_reset="latest",
                         enable_auto_commit=False,
                         value_deserializer=lambda m: json.loads(m.decode('ascii')))
    producer = KafkaProducer(bootstrap_servers=['su-broker:9192'])

    tp = TopicPartition('plc_updater', 0)
    consumer.assign([tp])

def test_sec_launch_software_update():
    req_id = uuid4().__str__()
    event_details = {
        'module_name': 'plc_control',
        'source': 'iam',
        'deliver_to': 'update_manager',
        'operation': 'launch_software_update',
        'id': req_id
    }  
    producer.send('monitor', key=event_details['id'].encode(), value=json.dumps(event_details).encode())
    consumer.poll()
    consumer.seek_to_end()

    partition = list(consumer.assignment())[0]
    end_offset = consumer.end_offsets([partition])
    consumer.seek(partition,max(0, list(end_offset.values())[0]-2))
    for message in consumer:
        if message.value['source'] == 'update_manager':
            assert  message.value['operation'] == 'request_software_update'
            break
    