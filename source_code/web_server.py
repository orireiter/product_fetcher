from pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from pyTools.extra_tools import get_conf, fix_json_quotings
from flask import Flask, request, jsonify

# Initialize the flask server and rabbit object
app = Flask(__name__)
rabbit = Rabbit(get_conf('RabbitMQ', 'host'))
# Declare the queues the the server is going to send messages to.
rabbit.declare_queue(
    get_conf('RabbitMQ', 'queues', 'amazon_queue'), durable=True)
rabbit.declare_queue(
    get_conf('RabbitMQ', 'queues', 'walmart_queue'), durable=True)
rabbit.declare_queue(
    get_conf('RabbitMQ', 'queues', 'db_reader_queue'), durable=True)
rabbit.declare_queue(
    get_conf('RabbitMQ', 'queues', 'db_writer_queue'), durable=True)



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
@app.route('/<string:source>/<string:_id>', methods=['GET'])
def get(source: str, _id: str):
    if source != "amazon" and source != "walmart":
        return("ERROR: source given must be either amazon or walmart."), 403
    else:
            result = rabbit.send_n_receive(
                get_conf('RabbitMQ', 'queues', f'{source}_queue'), _id)

            if result == ("b'None'"):
                return f"No product found for ID:{_id} in source:{source}", 404

            else:
                result = result.replace('b"', '').replace(
                    '"', '').replace('None', '"None"')
                result = fix_json_quotings(result)
                return jsonify(result)


app.run()
