import threading
from uuid import uuid4
from producer import proceed_to_deliver

device_event: threading.Event = None
POWER_RATIO = 20000 / 3000
POWER_THRESHOLD = 1000

TEMPERATURE_RATIO = 3000 / 50
TEMPERATURE_THRESHOLD = 5

settings: dict = {
    "min_power": 333, 
    "min_speed": 3, 
    "min_temperature": 5, 
    "max_power": 19999, 
    "max_speed": 2999, 
    "max_temperature": 49
}

sensor_readings = {
    'speed': 0,
    'temperature': 0,
    'power': 0
}

def alert(sensor):
    req_id = uuid4().__str__()
    details = {
        'deliver_to': 'scada_out',
        'operation': 'send_alert',
        'id': req_id
    }
    if 'speed' == sensor:
        details['description'] = f'[alert] speed value is \
            {sensor_readings["speed"]} when allowed range is \
                {settings["min_speed"]}:{settings["max_speed"]}'

    if 'power' == sensor:
        details['description'] = f'[alert] invalid power value is \
            {sensor_readings["power"]} when allowed range is \
                {settings["min_power"]}:{settings["max_power"]}'    
    
    if 'temperature' == sensor:
        details['description'] = f'[alert] invalid temperature value is \
            {sensor_readings["temperature"]} when allowed range is \
                {settings["min_temperature"]}:{settings["max_temperature"]}'   
    
    proceed_to_deliver(req_id, details)

def run_command(command):
    req_id = uuid4().__str__()
    if 'change_speed' in command:
        new_speed = sensor_readings["speed"] + int(command.get('change_speed'))
        details = {
            'new_speed': new_speed,
            'deliver_to': 'speed',
            'operation': 'change_speed'
        }
        proceed_to_deliver(req_id, details)
    device_event.set()

def update_settings(new_settings: dict):
    global settings, device_event
    if 'min_power' in new_settings:
        settings["min_power"] = new_settings.get('min_power')
    if 'max_power' in new_settings:
        settings["max_power"] = new_settings.get('max_power')
    if 'min_speed' in new_settings:
        settings["min_speed"] = new_settings.get('min_speed')
    if 'max_speed' in new_settings:
        settings["max_speed"] = new_settings.get('max_speed')
    if 'min_temperature' in new_settings:
        settings["min_temperature"] = new_settings.get('min_temperature')
    if 'max_temperature' in new_settings:
        settings["max_temperature"] = new_settings.get('max_temperature')
    device_event.set()

def update_sensor_readings(readings: dict):
    global sensor_readings, device_event
    if 'speed' in readings:
        sensor_readings["speed"] = readings.get('speed')
    if 'power' in readings:
        sensor_readings["power"] = readings.get('power')
    if 'temperature' in readings:
        sensor_readings["temperature"] = readings.get('temperature')
    device_event.set()

def processor_job():
    global device_event
    while True:
        device_event.wait()
        speed = sensor_readings["speed"]
        power = sensor_readings["power"] 
        temperature = sensor_readings["temperature"]

        if not (settings["min_speed"] <= sensor_readings["speed"] <= settings["max_speed"]):
            alert('speed')
        
        if (not (settings["min_power"] <= power <= settings["max_power"])) or \
            abs(power - speed * POWER_RATIO) > POWER_THRESHOLD:
            alert('power')

        if (not (settings["min_temperature"] <= temperature <= settings["max_temperature"])) or \
            abs(temperature - speed / TEMPERATURE_RATIO) > TEMPERATURE_THRESHOLD:
            alert('temperature')

        device_event.clear()


def start_processor():
    global device_event
    device_event = threading.Event()
    threading.Thread(target=lambda: processor_job()).start()

if __name__ == '__main__':
    start_processor(None)