from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf
from json import loads
import requests

# The RabbitMQ host to connect to,
# A queue to listen to,
# An API to query.
RABBIT_HOST = get_conf(['RabbitMQ', 'host'])
RABBIT_AMZN_QUEUE = get_conf(['RabbitMQ', 'queues', 'amzn_queue'])
AMZN_API = get_conf(["Amazon", "api"])


# Initializing a rabbit object and declaring the queue it will consume from.
amzn_fetcher = Rabbit(host=RABBIT_HOST)
amzn_fetcher.declare_queue(RABBIT_AMZN_QUEUE, durable=True)


# The function that will be executed when a message is consumed.
# It will use the ID in the msg to try and fetch
# info about a product from amazon.
def fetch_amzn_prdct(msg):
    # First, the message is decoded to string
    msg_as_str = msg.decode('utf-8')

    try:
        product = requests.get(AMZN_API+msg_as_str)
    except requests.exceptions.ConnectionError:
        return "ERROR: Couldn't connect to amazon API"

    # If the status code isn't 200, there was a problem.
    # Otherwise, the result (regarding the product)
    # is unpacked and is sent back to Rabbit.
    if product.status_code == 200:
        full_product_dict = loads(product.text)
        relevant_product_dict = {'id': msg_as_str,
                                 'title': full_product_dict["data"]["title"],
                                 'price': full_product_dict["data"]["price"],
                                 'source': 'amazon'
                                 }
        return relevant_product_dict
    else:
        return None


# This function starts listening to the given rabbit queue,
# and executes the function above upon message consumption, with
# the message as a parameter.
# The return of the callback function is sent back to RabbitMQ.
# For more information check the class docstrings.
amzn_fetcher.receive_n_send_many(RABBIT_AMZN_QUEUE, fetch_amzn_prdct)
