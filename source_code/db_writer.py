from pyTools.mongo import db_connect
from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf, fix_json_quotings
from json import loads


# The RabbitMQ host to connect to,
# A queue to listen to,
# The MongoDB host to connect to,
# A DB to query in MongoDB.
RABBIT_HOST = get_conf('RabbitMQ', 'host')
RABBIT_DB_WRITER_QUEUE = get_conf('RabbitMQ', 'queues', 'db_writer_queue')
MONGO_HOST = get_conf('MongoDB', 'host')+":"+"27017"
MONGO_DB = get_conf('MongoDB', 'db')


# After initializing a rabbit object and declare the queue it will consume from.
db_writer = Rabbit(host=RABBIT_HOST)
db_writer.declare_queue(RABBIT_DB_WRITER_QUEUE, durable=True)


# The function that will be executed when a message is consumed.
# It will turn the message into a dictionary and insert it to the DB.
def write_to_db(msg):
    # First, the message is decoded to string.
    # Then, since RabbitMQ messes with the qoutings
    # They're replaced as to not interrupt with
    # converting the string to a dict.
    msg_as_str = msg.decode('utf-8')
    msg_as_dict = fix_json_quotings(msg_as_str)
    
    # Assigning the collection according to the source of the product.
    # This is not a constant because this function will serve multiple
    # collections.
    collection = get_conf('MongoDB', 'collections', msg_as_dict['source'])

    # Creating a full connection string to the DB.
    mongo_connection = db_connect(MONGO_HOST, MONGO_DB, collection)

    # The dictionary is inserted into the collection.
    mongo_connection.insert_one(msg_as_dict)


# This function starts listening to the given rabbit queue,
# and executes the function above upon message consumption, with
# the message as a parameter.
db_writer.consume_many(RABBIT_DB_WRITER_QUEUE, write_to_db)
