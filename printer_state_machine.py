import json
import time

import requests


def main():
    base_url = 'http://172.31.1.225:5000/api/'
    api_key = 'AAA66DA914D847FF91CC48A8080B4D1C'
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }

    while True:
        response = requests.get(base_url + 'job', headers=headers)
        print(response.json())
        time.sleep(1)
    # filename = 'A.gcode'
    #
    # payload = {'command': 'select', 'print': 'false'}
    # url = base_url + 'files/local/' + filename
    #
    # response = requests.get(url, headers=headers, params=payload, data=json.dumps(payload))
    #
    # if response.status_code == 204:
    #     print(f"Successfully selected file: {filename}")
    # else:
    #     print(f"Error: Failed to select file: {filename}")
    #     print(f"Status code: {response.status_code}, Response: {response.text}")


if __name__ == "__main__":
    main()
