from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf
from json import loads
import requests


# After initializing a rabbit object and declare the queue it will consume from.
amzn_fetcher = Rabbit(host=get_conf(['RabbitMQ', 'host']))
amzn_fetcher.declare_queue(
    get_conf(['RabbitMQ', 'queues', 'amzn_queue']), durable=True)


# The function that will be executed when a message is consumed.
# It will use the ID in the msg try and fetch info about a product from amazon.
def fetch_amzn_prdct(msg):
    msg_as_str = msg.decode('utf-8')

    try:
        product = requests.get(
            f"https://ebazon-prod.herokuapp.com/ybl_assignment/amazon/{msg_as_str}")
    except requests.exceptions.ConnectionError:
        return "ERROR: Couldn't connect to amazon API"

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
amzn_fetcher.receive_n_send_many(
    get_conf(['RabbitMQ', 'queues', 'amzn_queue']), fetch_amzn_prdct)
