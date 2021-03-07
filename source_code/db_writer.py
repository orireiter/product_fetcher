from pyTools.mongo import db_connect
from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf
from json import loads

# After initializing a rabbit object and declare the queue it will consume from.
db_writer = Rabbit(host=get_conf(['RabbitMQ', 'host']))
db_writer.declare_queue(
    get_conf(['RabbitMQ', 'queues', 'db_writer_queue']), durable=True)


# The function that will be executed when a message is consumed.
# It will turn the message into a dictionary and insert it to the DB.
def write_to_db(msg):
    msg_as_str = msg.decode('utf-8')
    msg_as_str = msg_as_str.replace("'", '"')

    msg_as_dict = loads(msg_as_str)

    # Assigning the collection according to the source of the product.
    collection = get_conf(['MongoDB', 'collections', msg_as_dict['source']])
    mongo_connection = db_connect(get_conf(['MongoDB', 'host'])+":27017",
                                  get_conf(['MongoDB', 'db']), collection)
    mongo_connection.insert_one(msg_as_dict)


# This function starts listening to the given rabbit queue,
# and executes the function above upon message consumption, with
# the message as a parameter.
db_writer.consume_many(
    get_conf(['RabbitMQ', 'queues', 'db_writer_queue']), write_to_db)
