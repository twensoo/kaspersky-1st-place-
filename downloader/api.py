import os
import requests

host_name = "updates-server"
port = os.getenv("UPDATES_SERVER_PORT", default=5001)
endpoint = os.getenv("UPDATES_SERVER_ENDPOINT", default='download-update')
UPDATES_SERVER = f'http://{host_name}:{port}/{endpoint}'


def get_update(module_name: str):
    if len(module_name) > 0:
        try:
            res = requests.get(
                f"{UPDATES_SERVER}/{module_name}", allow_redirects=True)
            print(res.content)
            if res.status_code == 200:
                content = res.json()
                return content
        except Exception as e:
            error_message = f"can't download {e}"
            print(error_message)

    error_message = f"malformed request {module_name}"
    print(error_message)
