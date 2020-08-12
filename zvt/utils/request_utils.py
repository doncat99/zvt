# -*- coding: utf-8 -*-
import logging
from http import client
import requests
from requests.adapters import HTTPAdapter

from jqdatasdk import is_auth, auth, query, logout, \
                      get_fundamentals, get_mtss, get_fundamentals_continuously, \
                      get_all_securities, get_trade_days, get_bars
                      
from zvt import zvt_env

logger = logging.getLogger(__name__)

client.HTTPConnection._http_vsn=11
client.HTTPConnection._http_vsn_str='HTTP/1.1'

def get_http_session():
    http_session = requests.Session()
    http_session.mount('http://', HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=3))
    http_session.mount('https://', HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=3))
    return http_session

def request_get(http_session, url, headers=None):
    logger.info("HTTP GET: {}".format(url))
    return http_session.get(url, headers=headers, timeout=(5, 15))

def request_post(http_session, url, data=None, json=None):
    logger.info("HTTP POST: {}".format(url))
    return http_session.post(url=url, data=data, json=json, timeout=(5, 15))

def jq_auth():
    try:
        if not is_auth():
            auth(zvt_env['jq_username'], zvt_env['jq_password'])
        else:
            logger.info("already auth, attempt with {}:{}".format(zvt_env['jq_username'], zvt_env['jq_password']))
        return True
    except Exception as e:
        logger.warning(f'joinquant account not ok,the timestamp(publish date) for finance would be not correct', e)
    return False

def jq_logout():
    pass

def jq_query(*args, **kwargs):
    logger.info("HTTP QUERY")
    return query(*args, **kwargs)

def jq_get_fundamentals(query_object, date=None, statDate=None):
    logger.info("HTTP GET: fundamentals")
    return get_fundamentals(query_object, date=date, statDate=statDate)

def jq_get_mtss(security_list, start_date=None, end_date=None, fields=None, count=None):
    logger.info("HTTP GET: mtss")
    return get_mtss(security_list, start_date=start_date, end_date=end_date, fields=fields, count=count)

def jq_get_fundamentals_continuously(query_object, end_date=None, count=1, panel=True):
    logger.info("HTTP GET: fundamentals_continuously")
    return get_fundamentals_continuously(query_object, end_date=end_date, count=count, panel=panel)

def jq_get_all_securities(types=[], date=None):
    logger.info("HTTP GET: all_securities")
    return get_all_securities(types=types, date=date)

def jq_get_trade_days(start_date=None, end_date=None, count=None):
    logger.info("HTTP GET: trade_days")
    return get_trade_days(start_date=start_date, end_date=end_date, count=count)

def jq_get_bars(security, count, unit="1d", fields=("date", "open", "high", "low", "close"), include_now=False, end_dt=None,
             fq_ref_date=None, df=True):
    logger.info("HTTP GET: bars")
    return get_bars(security, count, unit=unit, fields=fields, include_now=include_now, 
                    end_dt=end_dt, fq_ref_date=fq_ref_date, df=df)