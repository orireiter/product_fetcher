import pytest
import requests

# POST_TESTS
#========================================================#


'''
    1 - a normal request that should work
    2 - a request with a non existing product ID
'''


@pytest.mark.parametrize('body,expected', [
    ('4837473', 200),
    ('ASFSVVV', 404),
    ('1!!?1', 403)
])
def test_walmart_fetcher(body, expected):

    result = requests.get(f'http://localhost/fetch/walmart/{body}')

    # Validate response headers and body contents, e.g. status code.
    assert result.status_code == expected
