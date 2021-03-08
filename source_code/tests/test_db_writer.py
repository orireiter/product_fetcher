from source_code.pyTools.RabbitMQ_Class.RabbitClass import Rabbit
from source_code.pyTools.extra_tools import get_conf
import pytest

# POST_TESTS
#========================================================#


'''
    1 - a normal request that should work
    2 - a request with a non existing product ID
'''


@pytest.mark.parametrize('body,expected', [
    ({"name": "ori", "gever": "ken", "source": "amazon"}, "None")
])
def test_db_writer(body, expected):

    rbt_conn = Rabbit(host=get_conf(['RabbitMQ', 'host']))
    rbt_conn.declare_queue(
        get_conf(['RabbitMQ', 'queues', 'db_writer_queue']), durable=True)

    result = rbt_conn.send_one(
        get_conf(['RabbitMQ', 'queues', 'db_writer_queue']), body)

    # Validate response headers and body contents, e.g. status code.
    assert result.replace("b'", "").replace("'", "") == expected