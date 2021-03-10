from pyTools.mongo import db_connect
from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf, wait_for_dependencies, is_configuration_n_rabbit_up
from json import loads


# doesn't start the app until the config file
# and rabbit are both available.
is_configuration_n_rabbit_up()


# The RabbitMQ host to connect to,
# A queue to listen to,
# The MongoDB host to connect to,
# A DB to query in MongoDB,
# A list of dependencies.
RABBIT_HOST = get_conf('rabbitmq', 'host')
RABBIT_DB_WRITER_QUEUE = get_conf('rabbitmq', 'queues', 'db_writer_queue')
MONGO_HOST = get_conf('mongodb', 'host')+":"+"27017"
MONGO_DB = get_conf('mongodb', 'db')
DEPENDS_ON = get_conf('db_writer', 'depends_on')

# waiting for dependencies before starting service
wait_for_dependencies(*DEPENDS_ON)


# After initializing a rabbit object and declare the queue it will consume from.
db_writer = Rabbit(host=RABBIT_HOST)
db_writer.declare_queue(RABBIT_DB_WRITER_QUEUE, durable=True)


# The function that will be executed when a message is consumed.
# It will turn the message into a dictionary and insert it to the DB.
def write_to_db(msg):
    # First, the message is loaded to a dict.
    msg_as_dict = loads(msg)

    # ensuring all IDs are strings ( to avoid errors and normalize IDs )
    msg_as_dict['_id'] = str(msg_as_dict['_id'])

    # Assigning the collection according to the source of the product.
    # This is not a constant because this function will serve multiple
    # collections.
    collection = get_conf('mongodb', 'collections', msg_as_dict['source'])

    # Creating a full connection string to the DB.
    mongo_connection = db_connect(MONGO_HOST, MONGO_DB, collection)
    try:
        # The dictionary is inserted into the collection.
        mongo_connection.insert_one(msg_as_dict)
    except:
        pass
        # should think how to fix this.


# This function starts listening to the given rabbit queue,
# and executes the function above upon message consumption, with
# the message as a parameter.
db_writer.consume_many(RABBIT_DB_WRITER_QUEUE, write_to_db)
