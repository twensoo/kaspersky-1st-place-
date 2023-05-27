import requests
import pytest
import json
import os

# ########## updates_server ##########

FILE_SERVER_HOST = None
FILE_SERVER_PORT = None

@pytest.fixture(autouse=True)
def env_preparing():
    global FILE_SERVER_HOST, FILE_SERVER_PORT 
    FILE_SERVER_HOST = "http://updates-server"
    FILE_SERVER_PORT = os.getenv("FILE_SERVER_PORT", default=5001)

def test_download_update():
    endpoint = 'download-update'
    module_name = 'plc_control'
    url = f'{FILE_SERVER_HOST}:{FILE_SERVER_PORT}/{endpoint}/{module_name}' 
    
    response = requests.get(url)

    assert 200 == response.status_code

def test_get_digest():
    endpoint = 'get-digest'
    module_name = 'plc_control'
    url = f'{FILE_SERVER_HOST}:{FILE_SERVER_PORT}/{endpoint}/{module_name}' 
    
    response = requests.get(url)
    
    assert 200 == response.status_code