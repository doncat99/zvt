# -*- coding: utf-8 -*-
import logging
from http import client
import requests
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

client.HTTPConnection._http_vsn=11
client.HTTPConnection._http_vsn_str='HTTP/1.1'

def get_http_session():
    http_session = requests.Session()
    http_session.mount('http://', HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=3))
    http_session.mount('https://', HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=3))
    return http_session

def request_get(http_session, url, headers=None):
    logger.info("GET: {}".format(url))
    return http_session.get(url, headers=headers, timeout=(5, 15))

def request_post(http_session, url, data=None, json=None):
    logger.info("POST: {}".format(url))
    return http_session.post(url=url, data=data, json=json, timeout=(5, 15))
