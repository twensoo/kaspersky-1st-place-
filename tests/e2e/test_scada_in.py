from uuid import uuid4
import requests
import pytest
import json
import os

SCADA_INPUT_HOST = None
SCADA_INPUT_API_PORT = None
operator_user: dict = None
observer_user: dict = None
engineer_user: dict = None

def _encrypt_decrypt(data: str, key: str):
    ld = len(data)
    lk = len(key)
    _data = str.encode(data)  
    _key = str.encode(key * (ld // lk) + key[:(ld % lk)])
    return str(bytearray(a^b for a, b in zip(*map(bytearray, [_data, _key])))) 

@pytest.fixture(autouse=True)
def env_preparing():
    print('[info] testing scada_in')
    global SCADA_INPUT_HOST, SCADA_INPUT_API_PORT, operator_user, observer_user, engineer_user
    SCADA_INPUT_HOST = "http://scada_in"
    SCADA_INPUT_API_PORT = os.getenv("SCADA_INPUT_API_PORT", default=6069)
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


def test_update_plc_software():
    endpoint = 'update_plc_software'
    url = f'{SCADA_INPUT_HOST}:{SCADA_INPUT_API_PORT}/{endpoint}'

    login = engineer_user['user']
    key = engineer_user['key']

    data = {
        'digest': uuid4().__str__(),
        'login': login
    }

    payload = {
        'user': login,
        'data': _encrypt_decrypt(json.dumps(data), key)
    }

    response = requests.post(url, json=payload)
    assert 200 == response.status_code

