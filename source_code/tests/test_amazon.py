import pytest
import requests

# POST_TESTS
#========================================================#


'''
    1 - a normal request that should work
    2 - a request with a non existing product ID
'''


@pytest.mark.parametrize('body,expected', [
    ('B071VG5N3151353D', 404),
    ('B07DQWT15Y', 200)
])
def test_amazon_fetcher(body, expected):

    result = requests.get(f'http://localhost/fetch/amazon/{body}')
    # Validate response headers and body contents, e.g. status code.
    assert result.status_code == expected
