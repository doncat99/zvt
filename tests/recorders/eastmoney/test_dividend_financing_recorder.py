# -*- coding: utf-8 -*-
from zvt.consts import SAMPLE_STOCK_CODES
from zvt.api.data_type import Region, Provider
from zvt.domain import DividendDetail, RightsIssueDetail, SpoDetail, DividendFinancing
from ...context import init_test_context

init_test_context()


def test_dividend_detail():
    try:
        DividendDetail.record_data(provider=Provider.EastMoney, codes=SAMPLE_STOCK_CODES)
    except:
        assert False


def test_rights_issue_detail():
    try:
        RightsIssueDetail.record_data(provider=Provider.EastMoney, codes=SAMPLE_STOCK_CODES)
    except:
        assert False


def test_spo_detail():
    try:
        SpoDetail.record_data(provider=Provider.EastMoney, codes=SAMPLE_STOCK_CODES)
    except:
        assert False


def test_dividend_financing():
    try:
        DividendFinancing.record_data(provider=Provider.EastMoney, codes=SAMPLE_STOCK_CODES)
    except:
        assert False
