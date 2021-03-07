from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf
from json import loads
import requests


# After initializing a rabbit object and declare the queue it will consume from.
wlmrt_fetcher = Rabbit(host=get_conf(['RabbitMQ', 'host']))
wlmrt_fetcher.declare_queue(
    get_conf(['RabbitMQ', 'queues', 'wlmrt_queue']), durable=True)


def fetch_wlmrt_prdct(msg):
    WLMRT_HEADERS = requests.get(
        "https://ebazon-prod.herokuapp.com/ybl_assignment/walmart/headers").text
    WLMRT_HEADERS = loads(WLMRT_HEADERS)
    WLMRT_HEADERS['data']['WM_SEC.KEY_VERSION'] = str(
        WLMRT_HEADERS['data']['WM_SEC.KEY_VERSION'])

    msg_as_str = msg.decode('utf-8')

    try:
        product = requests.get(
            f"https://developer.api.walmart.com/api-proxy/service/affil/product/v2/items/{msg_as_str}", headers=WLMRT_HEADERS["data"])
    except requests.exceptions.ConnectionError:
        return "ERROR: Couldn't connect to amazon API"

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
wlmrt_fetcher.receive_n_send_many(
    get_conf(['RabbitMQ', 'queues', 'wlmrt_queue']), fetch_wlmrt_prdct)


print(result)
