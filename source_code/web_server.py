import re
from json import loads, dumps
from flask import Flask, request, jsonify
from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf, wait_for_dependencies
from pyTools.extra_tools import is_configuration_n_rabbit_up


# doesn't start the app until the config file
# and rabbit are both available.
is_configuration_n_rabbit_up()


# The RabbitMQ host to connect to,
# A queue to listen to,
# An API to query,
# A list of json keys to be replaced with normalized
# keys used everywhere in this system,
# A list of dependencies.
RABBIT_HOST = get_conf('rabbitmq', 'host')
RABBIT_AMAZON_QUEUE = get_conf('rabbitmq', 'queues', 'amazon_queue')
RABBIT_WALMART_QUEUE = get_conf('rabbitmq', 'queues', 'walmart_queue')
RABBIT_DB_READER_QUEUE = get_conf('rabbitmq', 'queues', 'db_reader_queue')
RABBIT_DB_WRITER_QUEUE = get_conf('rabbitmq', 'queues', 'db_writer_queue')
RABBIT_DB_FILTER_QUEUE = get_conf('rabbitmq', 'queues', 'db_filter_queue')
RABBIT_RESPONSE_EXCHANGE = get_conf(
    'rabbitmq', 'exchanges', 'fetcher_writer_exchange')


# Initialize the flask server and rabbit object
app = Flask(__name__)
rabbit = Rabbit(get_conf('rabbitmq', 'host'))


# Declaring an exchange which will include writer, amazon + walmart fetcher.
# So that each message will return both to the client,
# and also be written to the db.
rabbit.declare_exchange(RABBIT_RESPONSE_EXCHANGE, 'topic')
rabbit.channel.queue_bind(rabbit.callback_queue,
                          RABBIT_RESPONSE_EXCHANGE, rabbit.callback_queue)


# Declare the queues the the server is going to send messages to.
rabbit.declare_queue(RABBIT_AMAZON_QUEUE, durable=True)
rabbit.declare_queue(RABBIT_WALMART_QUEUE, durable=True)
rabbit.declare_queue(RABBIT_DB_READER_QUEUE, durable=True)
rabbit.declare_queue(RABBIT_DB_WRITER_QUEUE, durable=True)


'''
    All the routes and requests require a database name and a table name.
    Otherwise you'll get a "page not found" error.
    Upon receiving a request, the server will first compare the db and table to the config file,
    so make sure to put all of the relevant info there!
    Then, depending if the method requires a db record id, the server will look for a JSON containing
    the info to post/get/update (and will look for an id in the url if needed).
    The server will then stringify the the info supplied and send it to the relevant rabbit queue,
    while waiting for an answer.
    A GET request willbe answered with the result of the query.
    The other requests (POST,DELETE,PUT) will be answered with the relevant record ID as a sign of success.
'''


@app.route('/fetch/<string:source>/<string:_id>', methods=['GET'])
def fetch_by_id(source: str, _id: str):
    # making sure the right urls are queried.
    if source != 'amazon' and source != 'walmart':
        return('ERROR: source given must be either amazon or walmart.'), 403
    # making sure the id contains only uppercase letter and numbers.
    elif not re.search(r'^[0-9A-Z]+$', str(_id)):
        return('ERROR: product ID given can contain only uppercase letters and numbers.'), 403
    else:
        # querying the db and if nothing there querying the web.
        record = rabbit.send_n_receive(RABBIT_DB_READER_QUEUE, dumps(
            {'_id': _id, 'source': source}))
        record = loads(record)

        if record == None:
            return jsonify({
                "error": "There are currently no listings for this product or could not fetch details about the product"
            }), 404
        else:
            return jsonify(record)


@app.route('/filter/<string:source>', methods=['GET'])
def filter_by_price(source: str):

    greater_than_or_equal = request.args.get('gte')
    lesser_than_or_equal = request.args.get('lte')

    # making sure the right urls are queried.
    if source != 'amazon' and source != 'walmart':
        return('ERROR: source given must be either amazon or walmart.'), 403
    # making sure the params contain only numbers
    # (since they're to check price).
    elif not re.search(r'^[0-9]+$', str(greater_than_or_equal)):
        return('ERROR: price values can contain only numbers.'), 403
    elif not re.search(r'^[0-9]+$', str(lesser_than_or_equal)):
        return('ERROR: price values can contain only numbers.'), 403
    else:
        # querying the db and returning the response.
        record = rabbit.send_n_receive(RABBIT_DB_FILTER_QUEUE, dumps(
            {'$gte': int(greater_than_or_equal),
             '$lte': int(lesser_than_or_equal),
             'source': source}))
        record = loads(record)
        return jsonify(record)
