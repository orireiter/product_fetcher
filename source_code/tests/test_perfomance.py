import requests
import pytest
import time
import multiprocessing
import json

#========================================================#
# PERFORMANCE_TESTS
#========================================================#


def send_req():
    url = 'http://localhost/fetch/amazon/B07DQWT15Y'
    resp = requests.get(url=url)

def test_performance_many_at_once():
    start_time = time.time()

    pool = multiprocessing.Pool()
    for _ in range(500):
        pool.apply_async(send_req)
    pool.close()
    pool.join()

    elapsed_time = time.time() - start_time
    assert elapsed_time <= 15