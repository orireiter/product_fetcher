from pyTools.extra_tools import get_conf
from json import loads, dump
from time import sleep
import requests


# An API to query for walmart headers.
# A path to a json file containing headers to add to an api request.
WLMRT_HEADERS_API = get_conf(['Walmart', 'headers_api'])
WLMRT_HEADERS_JSON_PATH = get_conf(['Walmart', 'headers_json'])


# This function queries an API that retrieves headers_api
# Which later on will be used as headers to query Walmart's APi.
# The TTL of these headers is 180 seconds, meaning - it's enough to reaquire them
# every 60 seconds.
def fetch_wlmrt_headers():
    while True:
        try:
            # Querying the api.
            WLMRT_HEADERS = requests.get(WLMRT_HEADERS_API)

            # If the status code is 200, it's 
            # safe to assume a JSON was received.
            # The json will be converted to a dictionary 
            # ( to make sure all values are strings )
            # the dictionary will be dumped into a json file.
            if WLMRT_HEADERS.status_code == 200:
                WLMRT_HEADERS = loads(WLMRT_HEADERS.text)
                WLMRT_HEADERS['data']['WM_SEC.KEY_VERSION'] = str(
                    WLMRT_HEADERS['data']['WM_SEC.KEY_VERSION'])

                with open(WLMRT_HEADERS_JSON_PATH, 'w') as file:
                    dump(WLMRT_HEADERS['data'], file)
            else:
                print("Status code wasn't 200 OK, "
                "will try to reconnect in 60 seconds.")

        except requests.exceptions.ConnectionError:
            print("couldn't reach the headers' API, "
            "will try to reconnect in 60 seconds.")

        sleep(60)


fetch_wlmrt_headers()
