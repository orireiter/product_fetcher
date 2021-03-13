import requests
import datetime
from json import loads, dumps
from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import wait_for_dependencies, is_configuration_n_rabbit_up
from pyTools.extra_tools import get_conf, dictionary_key_repacker


# doesn't start the app until the config file
# and rabbit are both available.
is_configuration_n_rabbit_up()


# The RabbitMQ host to connect to,
# A queue to listen to,
# An API to query,
# A list of json keys to be replaced with normalized
# keys used everywhere in this system.
# A list of dependencies
RABBIT_HOST = get_conf('rabbitmq', 'host')
RABBIT_AMAZON_QUEUE = get_conf('rabbitmq', 'queues', 'amazon_queue')
RABBIT_RESPONSE_EXCHANGE = get_conf(
    'rabbitmq', 'exchanges', 'fetcher_writer_exchange')
AMAZON_API = get_conf('amazon', 'api')
AMAZON_JSON_KEYS = get_conf('amazon', 'keys')
DEPENDS_ON = get_conf('amazon', 'depends_on')

# waiting for dependencies before starting service
wait_for_dependencies(*DEPENDS_ON)


# Initializing a rabbit object and declaring the queue it will consume from.
amazon_fetcher = Rabbit(host=RABBIT_HOST)
amazon_fetcher.declare_queue(RABBIT_AMAZON_QUEUE, durable=True)


# The function that will be executed when a message is consumed.
# It will use the ID in the msg to try and fetch
# info about a product from amazon.
def fetch_amazon_product(msg):

    try:
        msg_as_dict = loads(msg)
        # only the id value is needed to query the remote db.
        msg_id = msg_as_dict['_id']

        product = requests.get(AMAZON_API+msg_id)
    except requests.exceptions.ConnectionError:
        print(f'{datetime.datetime.now()} -> ERROR: Couldn\'t connect'
              f'to amazon API with {msg_as_dict}')
        return dumps(None)

    # If the status code isn't 200, there was a problem.
    # Otherwise, the result (regarding the product)
    # is unpacked and is sent back to Rabbit.
    if product.status_code == 200:
        full_product_dict = loads(product.text)['data']
        relevant_product_dict = dictionary_key_repacker(
            full_product_dict, AMAZON_JSON_KEYS)

        # certain values are normalized before writing to db.
        relevant_product_dict['source'] = msg_as_dict['source']
        relevant_product_dict['_id'] = str(relevant_product_dict['_id'])
        return dumps(relevant_product_dict)
    else:
        return dumps(None)


# This function starts listening to the given rabbit queue,
# and executes the function above upon message consumption, with
# the message as a parameter.
# The return of the callback function is sent back to RabbitMQ.
# For more information check the class docstrings.
amazon_fetcher.receive_n_send_many(
    RABBIT_AMAZON_QUEUE, fetch_amazon_product, RABBIT_RESPONSE_EXCHANGE)
