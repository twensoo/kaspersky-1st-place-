from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from uuid import uuid4
import pytest
import json

consumer: KafkaConsumer = None
producer: KafkaProducer = None

@pytest.fixture(autouse=True)
def plc_control_env_preparing():
    global consumer, producer
    consumer = KafkaConsumer(
                         group_id='tester',
                         bootstrap_servers=['su-broker:9192'],
                         auto_offset_reset="latest",
                         enable_auto_commit=False,
                         value_deserializer=lambda m: json.loads(m.decode('ascii')))
    producer = KafkaProducer(bootstrap_servers=['su-broker:9192'])

    tp = TopicPartition('scada_out', 0)
    consumer.assign([tp])

def test_sec_push_speed_value():
    req_id = uuid4().__str__()
    event_details = {
        'speed': 1500,
        'source': 'plc_control',
        'deliver_to': 'scada_out',
        'operation': 'push_speed_value',
        'id': req_id
    }  
    producer.send('monitor', key=event_details['id'].encode(), value=json.dumps(event_details).encode())
    consumer.poll()
    consumer.seek_to_end()

    partition = list(consumer.assignment())[0]
    end_offset = consumer.end_offsets([partition])
    consumer.seek(partition,max(0, list(end_offset.values())[0]-2))
    for message in consumer:
        if message.value['source'] == 'plc_control':
            assert  message.value['speed'] == event_details['speed']
            break
    