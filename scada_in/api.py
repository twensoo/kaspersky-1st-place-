from flask import Flask, request, jsonify
from uuid import uuid4
import os
from dotenv import load_dotenv
import threading
from producer import proceed_to_deliver

load_dotenv()

host_name = "0.0.0.0"
port = os.getenv("SCADA_INPUT_API_PORT", default=6069)

app = Flask(__name__)             # create an app instance

@app.route("/<operation>", methods=['POST'])
def handle_query(operation):
    operations = {'update_plc_software', 'run_command', 'change_settings', 'hard_stop'}
    if operation in operations:
        req_id = uuid4().__str__()
        try:
            content = request.json
            details = {
                "id": req_id,
                "operation": operation,
                "user": content['user'],
                "data": content['data'],
                "deliver_to": "iam"
            }
            proceed_to_deliver(req_id, details)
            print(f"new input event: {details}")
        except:
            error_message = f"malformed request {request.data}"
            print(error_message)
            return jsonify(error_message), 400
        return jsonify({"operation": "new data received", "id": req_id})
    error_message = f"malformed request {request.data}"
    print(error_message)
    return jsonify(error_message), 400


def start_rest():
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()