import pytest
import requests


@pytest.mark.parametrize('body,expected', [
    (['0', '150'], 200),
    (['A', '200'], 403)
])
def test_amazon_fetcher(body, expected):

    result = requests.get(f'http://localhost/filter/walmart?gte={body[0]}&lte={body[1]}')
    # Validate response headers and body contents, e.g. status code.
    assert result.status_code == expected


