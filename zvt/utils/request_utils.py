# -*- coding: utf-8 -*-
import requests
from requests.adapters import HTTPAdapter

def get_http_session():
    http_session = requests.Session()
    http_session.mount('http://', HTTPAdapter(max_retries=3))
    http_session.mount('https://', HTTPAdapter(max_retries=3))
    return http_session

def request_get(http_session, url, headers=None):
    # print("*********** get ****************", http_session)
    return http_session.get(url, timeout=(5, 10), headers=headers)

def request_post(http_session, url, data=None, json=None):
    # print("*********** post ****************", http_session)
    return http_session.post(url=url, data=data, json=json, timeout=(5, 10))
