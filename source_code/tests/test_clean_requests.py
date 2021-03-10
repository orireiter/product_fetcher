import pytest
import requests
from source_code.pyTools.extra_tools import get_conf


# POST_TESTS
#========================================================#


'''
    1 - a normal request that should work
    2 - a request with a non existing product ID
'''


@pytest.mark.parametrize('body,expected', [
    ('B07DQWT15Y', 'None')
])
def test_clean_req(body, expected):
    result = requests.get(
        f'https://ebazon-prod.herokuapp.com/ybl_assignment/amazon/{body}').text

    # Validate response headers and body contents, e.g. status code.
    assert result.replace('b', '').replace("'", '') == expected
