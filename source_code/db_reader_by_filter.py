import datetime
from json import loads, dumps
from pyTools.mongo import db_connect
from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf, wait_for_dependencies
from pyTools.extra_tools import is_configuration_n_rabbit_up


# doesn't start the app until the config file
# and rabbit are both available.
is_configuration_n_rabbit_up()


# The RabbitMQ host to connect to,
# A queue to listen to,
# The MongoDB host to connect to,
# A DB to query in MongoDB,
# A list of dependencies.
RABBIT_HOST = get_conf('rabbitmq', 'host')
RABBIT_DB_FILTER_QUEUE = get_conf('rabbitmq', 'queues', 'db_filter_queue')
MONGO_HOST = get_conf('mongodb', 'host')+':27017'
MONGO_DB = get_conf('mongodb', 'db')
DEPENDS_ON = get_conf('db_filter', 'depends_on')

# waiting for dependencies before starting service
wait_for_dependencies(*DEPENDS_ON)


# Initializing a rabbit object and declaring the queue it will consume from.
db_reader = Rabbit(host=RABBIT_HOST)
db_reader.declare_queue(RABBIT_DB_FILTER_QUEUE, durable=True)


# The function that will be executed when a message is consumed.
# It will turn the message into a dictionary and query the DB with it.
def filter_from_db(msg):
    try:
        # First, the message is loaded to a dict.
        msg_as_dict = loads(msg)

        # Assigning the collection according to the source of the product.
        # This is not a constant because this function will serve multiple
        # collections.
        # At the same time, the source is popped, this 
        # leaves only 'greater' and 'lesser', which are used to query the price.
        collection = get_conf('mongodb', 'collections', msg_as_dict.pop('source'))

        # Creating a full connection string to the DB.
        mongo_connection = db_connect(MONGO_HOST, MONGO_DB, collection)

        # The DB is queried with the msg dictionary as a filter.
        results = mongo_connection.find(
            {'price': msg_as_dict}, projection={'ttl': False})
    except:
        print(f'{datetime.datetime.now()} -> ERROR: couldn\'t contact'
        f' mongo db with {msg}')
        results = [None]

    # The results are returned in a list.
    return dumps([result for result in results])


# This function starts listening to the given rabbit queue,
# and executes the function above upon message consumption, with
# the message as a parameter.
# The return of the callback function is sent back to RabbitMQ.
# For more information check the class docstrings.
db_reader.receive_n_send_many(RABBIT_DB_FILTER_QUEUE, filter_from_db)
