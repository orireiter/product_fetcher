from json import loads
import datetime
from pyTools.mongo import db_connect, create_ttl_in_collections
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
RABBIT_DB_WRITER_QUEUE = get_conf('rabbitmq', 'queues', 'db_writer_queue')
RABBIT_RESPONSE_EXCHANGE = get_conf(
    'rabbitmq', 'exchanges', 'fetcher_writer_exchange')
MONGO_HOST = get_conf('mongodb', 'host')+':27017'
MONGO_DB = get_conf('mongodb', 'db')
MONGO_TTL = get_conf('mongodb', 'ttl')
DEPENDS_ON = get_conf('db_writer', 'depends_on')


# waiting for dependencies before starting service
wait_for_dependencies(*DEPENDS_ON)


# After initializing a rabbit object and declare the queue it will consume from.
db_writer = Rabbit(host=RABBIT_HOST)
db_writer.declare_queue(RABBIT_DB_WRITER_QUEUE, durable=True)


# Declaring an exchange which will include writer, amazon + walmart fetcher.
# So that each message will return both to the client,
# and also be written to the db.
db_writer.declare_exchange(RABBIT_RESPONSE_EXCHANGE, 'topic')
db_writer.channel.queue_bind(
    RABBIT_DB_WRITER_QUEUE, RABBIT_RESPONSE_EXCHANGE, '#')


# A ttl index is inserted to the collections
for collection in get_conf('mongodb', 'collections').values():
    create_ttl_in_collections('ttl', MONGO_TTL, db_connect(
        MONGO_HOST, MONGO_DB, collection))


# The function that will be executed when a message is consumed.
# It will turn the message into a dictionary and insert it to the DB.
def write_to_db(msg):
    try:
        # First, the message is loaded to a dict.
        msg_as_dict = loads(msg)

        # since every message that went to walmart/amazon
        # also goes here, this is to ensure when they return the an
        # id doesn't exist, it's not written to the db or crashes
        # this consumer.
        if msg_as_dict == None:
            return None
        # ensuring all IDs are strings ( to avoid errors and normalize IDs )
        # adding a ttl.
        msg_as_dict['_id'] = str(msg_as_dict['_id'])
        msg_as_dict['ttl'] = datetime.datetime.utcnow()

        # Assigning the collection according to the source of the product.
        # This is not a constant because this function will serve multiple
        # collections.
        collection = get_conf('mongodb', 'collections', msg_as_dict['source'])

        # Creating a full connection string to the DB.
        mongo_connection = db_connect(MONGO_HOST, MONGO_DB, collection)
        
        # The dictionary is inserted into the collection.
        mongo_connection.insert_one(msg_as_dict)
    except:
        print(f'{datetime.datetime.now()} -> Couldn\'t write {msg}')
        # should think how to fix this.


# This function starts listening to the given rabbit queue,
# and executes the function above upon message consumption, with
# the message as a parameter.
db_writer.consume_many(RABBIT_DB_WRITER_QUEUE, write_to_db)
