# -*- coding: utf-8 -*-
from zvt.contract import IntervalLevel
from zvt.api.quote import get_kdata
from zvt.api.quote import to_high_level_kdata, get_recent_report_date
from ..context import init_test_context

init_test_context()


def test_to_high_level_kdata():
    day_df = get_kdata(provider='joinquant', level=IntervalLevel.LEVEL_1DAY, entity_id='stock_sz_000338')
    print(day_df)

    df = to_high_level_kdata(kdata_df=day_df.loc[:'2019-09-01', :], to_level=IntervalLevel.LEVEL_1WEEK)

    print(df)


def test_get_recent_report_date():
    assert '2018-12-31' == get_recent_report_date('2019-01-01', 0)
    assert '2018-09-30' == get_recent_report_date('2019-01-01', 1)
    assert '2018-06-30' == get_recent_report_date('2019-01-01', 2)
    assert '2018-03-31' == get_recent_report_date('2019-01-01', 3)
