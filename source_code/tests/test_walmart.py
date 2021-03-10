import pytest
from source_code.pyTools.extra_tools import get_conf
from source_code.pyTools.RabbitMQ_Class.RabbitClass import Rabbit


# POST_TESTS
#========================================================#


'''
    1 - a normal request that should work
    2 - a request with a non existing product ID
'''


@pytest.mark.parametrize('body,expected', [
    ('4837473', 'None')
])
def test_walmart_fetcher(body, expected):

    rbt_conn = Rabbit(host=get_conf('rabbitmq', 'host'))
    rbt_conn.declare_queue(
        get_conf('rabbitmq', 'queues', 'walmart_queue'), durable=True)

    result = rbt_conn.send_n_receive(
        get_conf('rabbitmq', 'queues', 'walmart_queue'), body)

    # Validate response headers and body contents, e.g. status code.
    assert result.replace('b', '').replace("'", '') == expected
