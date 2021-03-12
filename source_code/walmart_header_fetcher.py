import requests
from time import sleep
from json import loads, dump
from pyTools.extra_tools import get_conf


# An API to query for walmart headers.
# A path to a json file containing headers to add to an api request.
WALMART_HEADERS_API = get_conf('walmart', 'headers_api')
WALMART_HEADERS_JSON_PATH = get_conf('walmart', 'headers_json')
FETCH_INTERVAL = get_conf('walmart', 'headers_fetch_interval')

# This function queries an API that retrieves headers_api
# Which later on will be used as headers to query Walmart's APi.
# The TTL of these headers is 180 seconds, meaning - it's enough to reaquire them
# every 60 seconds.
def fetch_walmart_headers(headers_api: str, file_to_write_to: str, interval: int):
    while True:
        try:
            # Querying the api.
            walmart_headers = requests.get(headers_api)

            # If the status code is 200, it's
            # safe to assume a JSON was received.
            # The json will be converted to a dictionary
            # ( to make sure all values are strings )
            # the dictionary will be dumped into a json file.
            if walmart_headers.status_code == 200:
                walmart_headers = loads(walmart_headers.text)
                walmart_headers['data']['WM_SEC.KEY_VERSION'] = str(
                    walmart_headers['data']['WM_SEC.KEY_VERSION'])

                with open(file_to_write_to, 'w') as file:
                    dump(walmart_headers['data'], file)
            else:
                print("Status code wasn't 200 OK, "
                      "will try to reconnect in 60 seconds.")

        except requests.exceptions.ConnectionError:
            print("couldn't reach the headers' API, "
                  "will try to reconnect in 60 seconds.")

        sleep(interval)


fetch_walmart_headers(WALMART_HEADERS_API, WALMART_HEADERS_JSON_PATH, FETCH_INTERVAL)
