from flask import Flask, request, jsonify
from dotenv import load_dotenv
from uuid import uuid4
import threading
import os
from producer import proceed_to_deliver

load_dotenv()

host_name = "0.0.0.0"
port = os.getenv("LICENSE_SERVER_PORT", default=6067)

digests: set = None

app = Flask(__name__)             # create an app instance

def add_digest(digest):
    global digests
    digests.add(digest)

@app.route("/", methods=['POST'])
def check_seal():
    details = {
        'valid': False
    }
    try:
        content = request.json
        digest = content['digest']
        if digest in digests:
            details["valid"] = True
    except:
        error_message = f"malformed request {request.data}"
        print(error_message)
    return jsonify(details)


def start_rest():
    global digests
    digests = set()
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()