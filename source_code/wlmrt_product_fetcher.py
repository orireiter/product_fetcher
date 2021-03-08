from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf
from json import loads
import requests


# The RabbitMQ host to connect to,
# A queue to listen to,
# An API to query.
# A json file containing headers required.
RABBIT_HOST = get_conf(['RabbitMQ', 'host'])
RABBIT_WLMRT_QUEUE = get_conf(['RabbitMQ', 'queues', 'wlmrt_queue'])
WLMRT_API = get_conf(["Walmart", "api"])
WLMRT_HEADERS_JSON = get_conf(["Walmart", "headers_json"])

# After initializing a rabbit object and declare the queue it will consume from.
wlmrt_fetcher = Rabbit(host=RABBIT_HOST)
wlmrt_fetcher.declare_queue(RABBIT_WLMRT_QUEUE, durable=True)


# The function that will be executed when a message is consumed.
# It will use the ID in the msg to try and fetch
# info about a product from walmart.
def fetch_wlmrt_prdct(msg):
    # First the json containing headers is loaded.
    with open(WLMRT_HEADERS_JSON, "r") as file:
        WLMRT_HEADERS = loads(file.read())

    # Second, the message is decoded to string
    msg_as_str = msg.decode('utf-8')

    # The API is queried, along with the headers.
    try:
        product = requests.get(WLMRT_API + msg_as_str, headers=WLMRT_HEADERS)
    except requests.exceptions.ConnectionError:
        return "ERROR: Couldn't connect to amazon API"

    # If the status code isn't 200, there was a problem.
    # Otherwise, the result (regarding the product)
    # is unpacked and is sent back to Rabbit.
    if product.status_code == 200:
        full_product_dict = loads(product.text)
        relevant_product_dict = {"id": msg_as_str, "name": full_product_dict["name"],
                                 "price": full_product_dict["salePrice"], "source": "walmart"}

        return relevant_product_dict

    else:
        return None


# This function starts listening to the given rabbit queue,
# and executes the function above upon message consumption, with
# the message as a parameter.
# The return of the callback function is sent back to RabbitMQ.
# For more information check the class docstrings.
wlmrt_fetcher.receive_n_send_many(RABBIT_WLMRT_QUEUE, fetch_wlmrt_prdct)
