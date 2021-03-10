from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf, dictionary_repacker
from json import loads, dumps
import requests


# The RabbitMQ host to connect to,
# A queue to listen to,
# An API to query.
# A json file containing headers required,
# A list of json keys to be replaced with normalized
# keys used everywhere in this system.
RABBIT_HOST = get_conf('RabbitMQ', 'host')
RABBIT_WALMART_QUEUE = get_conf('RabbitMQ', 'queues', 'walmart_queue')
WALMART_API = get_conf("Walmart", "api")
WALMART_HEADERS_JSON = get_conf("Walmart", "headers_json")
WALMART_JSON_KEYS = get_conf("Walmart", "keys")


# After initializing a rabbit object and declare the queue it will consume from.
wlmrt_fetcher = Rabbit(host=RABBIT_HOST)
wlmrt_fetcher.declare_queue(RABBIT_WALMART_QUEUE, durable=True)


# The function that will be executed when a message is consumed.
# It will use the ID in the msg to try and fetch
# info about a product from walmart.
def fetch_walmart_prdct(msg):
    # First the json containing headers is loaded.
    with open(WALMART_HEADERS_JSON, "r") as file:
        walmart_headers = loads(file.read())

    # The API is queried, along with the headers.
    try:
        product = requests.get(WALMART_API + msg,
                               headers=walmart_headers)
    except requests.exceptions.ConnectionError:
        return "ERROR: Couldn't connect to amazon API"

    # If the status code isn't 200, there was a problem.
    # Otherwise, the result (regarding the product)
    # is unpacked and is sent back to Rabbit.
    if product.status_code == 200:
        full_product_dict = loads(product.text)
        relevant_product_dict = dictionary_repacker(
            full_product_dict, WALMART_JSON_KEYS)

        return dumps(relevant_product_dict)

    else:
        return None


# This function starts listening to the given rabbit queue,
# and executes the function above upon message consumption, with
# the message as a parameter.
# The return of the callback function is sent back to RabbitMQ.
# For more information check the class docstrings.
wlmrt_fetcher.receive_n_send_many(RABBIT_WALMART_QUEUE, fetch_walmart_prdct)
