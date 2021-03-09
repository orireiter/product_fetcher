from pyTools.extra_tools import get_conf
from json import loads, dump
from time import sleep
import requests


# An API to query for walmart headers.
# A path to a json file containing headers to add to an api request.
WALMART_HEADERS_API = get_conf('Walmart', 'headers_api')
WALMART_HEADERS_JSON_PATH = get_conf('Walmart', 'headers_json')


# This function queries an API that retrieves headers_api
# Which later on will be used as headers to query Walmart's APi.
# The TTL of these headers is 180 seconds, meaning - it's enough to reaquire them
# every 60 seconds.
def fetch_walmart_headers():
    while True:
        try:
            # Querying the api.
            WALMART_HEADERS = requests.get(WALMART_HEADERS_API)

            # If the status code is 200, it's
            # safe to assume a JSON was received.
            # The json will be converted to a dictionary
            # ( to make sure all values are strings )
            # the dictionary will be dumped into a json file.
            if WALMART_HEADERS.status_code == 200:
                WALMART_HEADERS = loads(WALMART_HEADERS.text)
                WALMART_HEADERS['data']['WM_SEC.KEY_VERSION'] = str(
                    WALMART_HEADERS['data']['WM_SEC.KEY_VERSION'])

                with open(WALMART_HEADERS_JSON_PATH, 'w') as file:
                    dump(WALMART_HEADERS['data'], file)
            else:
                print("Status code wasn't 200 OK, "
                      "will try to reconnect in 60 seconds.")

        except requests.exceptions.ConnectionError:
            print("couldn't reach the headers' API, "
                  "will try to reconnect in 60 seconds.")

        sleep(60)


fetch_walmart_headers()
