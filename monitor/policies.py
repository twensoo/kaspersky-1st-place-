from hashlib import sha256
import requests
import os
import json

host_name = "0.0.0.0"
port = os.getenv("LICENSE_SERVER_PORT", default=6067)
endpoint = os.getenv("LICENSE_SERVER_ENDPOINT", default='check_seal')
LICENSE_SERVER = f'http://{host_name}:{port}/{endpoint}'
CONTENT_HEADER = {"Content-Type": "application/json"}

def check_operation(id, details):
    authorized = False
    # print(f"[debug] checking policies for event {id}, details: {details}")
    print(f"[info] checking policies for event {id},"
          f" {details['source']}->{details['deliver_to']}: {details['operation']}")
    src = details['source']
    dst = details['deliver_to']
    operation = details['operation']

    policies = [
        { 'dst': 'cutoff',         'src': 'iam',            'operation': 'hard_stop'},
        { 'dst': 'cutoff',         'src': 'iam',            'operation': 'hard_stop'},
        { 'dst': 'downloader',     'src': 'update_manager', 'operation': 'request_download'},
        { 'dst': 'iam',            'src': 'scada_in',       'operation': 'update_plc_software'},
        { 'dst': 'iam',            'src': 'scada_in',       'operation': 'run_command'},
        { 'dst': 'iam',            'src': 'scada_in',       'operation': 'change_settings'},
        { 'dst': 'iam',            'src': 'scada_in',       'operation': 'hard_stop'},
        { 'dst': 'iam',            'src': 'scada_out',      'operation': 'check_user'},
        { 'dst': 'iam',            'src': 'keygen',         'operation': 'send_keys'},
        { 'dst': 'keygen',         'src': 'iam',            'operation': 'generate_keys'},
        { 'dst': 'license_server', 'src': 'iam',            'operation': 'new_update_digest'},
        { 'dst': 'plc_analog',     'src': 'temperature',    'operation': 'push_temperature_value'},
        { 'dst': 'plc_analog',     'src': 'power',          'operation': 'push_power_value'},
        { 'dst': 'plc_control',    'src': 'iam',            'operation': 'run_command'},
        { 'dst': 'plc_control',    'src': 'iam',            'operation': 'change_settings'},
        { 'dst': 'plc_control',    'src': 'plc_digital',    'operation': 'push_speed_value'},
        { 'dst': 'plc_control',    'src': 'plc_analog',     'operation': 'push_temperature_value'},
        { 'dst': 'plc_control',    'src': 'plc_analog',     'operation': 'push_power_value'},
        { 'dst': 'plc_digital',    'src': 'speed',          'operation': 'push_speed_impulse'},
        { 'dst': 'plc_updater',    'src': 'storage',        'operation': 'send_software_update'},
        { 'dst': 'plc_updater',    'src': 'update_manager', 'operation': 'request_software_update'},
        { 'dst': 'scada_out',      'src': 'iam',            'operation': 'authorize_user'},
        { 'dst': 'scada_out',      'src': 'plc_control',    'operation': 'push_speed_value'},
        { 'dst': 'scada_out',      'src': 'plc_control',    'operation': 'send_alert'},
        { 'dst': 'scada_out',      'src': 'temperature',    'operation': 'push_temperature_value'},
        { 'dst': 'scada_out',      'src': 'power',          'operation': 'push_power_value'},
        { 'dst': 'speed',          'src': 'plc_control',    'operation': 'change_speed'},
        { 'dst': 'speed',          'src': 'cutoff',         'operation': 'shutdown'},
        { 'dst': 'storage',        'src': 'plc_updater',    'operation': 'get_software_update'},
        { 'dst': 'storage',        'src': 'downloader',     'operation': 'save_file'},
        { 'dst': 'update_manager', 'src': 'iam',            'operation': 'launch_software_update'},
        { 'dst': 'update_manager', 'src': 'downloader',     'operation': 'report_downloaded'}
    ]

    if {'dst': dst, 'src': src, 'operation': operation} in policies:
        authorized = True
        if operation == "send_software_update" and check_payload_seal(details['blob']) is False:
            authorized = False

    print(f"[info] event {id} is authorized: {authorized}")

    return authorized

def generate_digest(payload):
    BUF_SIZE = 65536
    digest = sha256()

    digest.update(payload[:BUF_SIZE])

    return digest.hexdigest()

def check_payload_seal(payload):
    try:
        digest = { 'digest': generate_digest(payload) }
        result = requests.post(
             LICENSE_SERVER,
             data=json.dumps(digest),
             headers=CONTENT_HEADER).json()
        return result['valid']
    except Exception as e:
        print(f'[error] seal check error: {e}')
        return False