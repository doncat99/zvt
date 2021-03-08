# -*- coding: utf-8 -*-
from zvt.contract import IntervalLevel
from zvt.utils.time_utils import eval_size_of_timestamp, next_timestamp, to_pd_timestamp, \
    is_finished_kdata_timestamp, split_time_interval, is_same_date


def test_evaluate_size_from_timestamp():
    size = eval_size_of_timestamp(start_timestamp='2019-01-01', end_timestamp='2019-01-02',
                                        level=IntervalLevel.LEVEL_1MON, one_day_trading_minutes=4 * 60)

    assert size == 2

    size = eval_size_of_timestamp(start_timestamp='2019-01-01', end_timestamp='2019-01-02',
                                        level=IntervalLevel.LEVEL_1WEEK, one_day_trading_minutes=4 * 60)

    assert size == 2

    size = eval_size_of_timestamp(start_timestamp='2019-01-01', end_timestamp='2019-01-02',
                                        level=IntervalLevel.LEVEL_1DAY, one_day_trading_minutes=4 * 60)

    assert size == 2

    size = eval_size_of_timestamp(start_timestamp='2019-01-01', end_timestamp='2019-01-02',
                                        level=IntervalLevel.LEVEL_1HOUR, one_day_trading_minutes=4 * 60)

    assert size == 9

    size = eval_size_of_timestamp(start_timestamp='2019-01-01', end_timestamp='2019-01-02',
                                        level=IntervalLevel.LEVEL_1MIN, one_day_trading_minutes=4 * 60)

    assert size == 481


def test_next_timestamp():
    current = '2019-01-10 13:15'
    assert next_timestamp(current, level=IntervalLevel.LEVEL_1MIN) == to_pd_timestamp('2019-01-10 13:16')
    assert next_timestamp(current, level=IntervalLevel.LEVEL_5MIN) == to_pd_timestamp('2019-01-10 13:20')
    assert next_timestamp(current, level=IntervalLevel.LEVEL_15MIN) == to_pd_timestamp('2019-01-10 13:30')


def test_is_finished_kdata_timestamp():
    timestamp = '2019-01-10 13:05'
    assert not is_finished_kdata_timestamp(timestamp, level=IntervalLevel.LEVEL_1DAY)
    assert not is_finished_kdata_timestamp(timestamp, level=IntervalLevel.LEVEL_1HOUR)
    assert not is_finished_kdata_timestamp(timestamp, level=IntervalLevel.LEVEL_30MIN)
    assert not is_finished_kdata_timestamp(timestamp, level=IntervalLevel.LEVEL_15MIN)
    assert is_finished_kdata_timestamp(timestamp, level=IntervalLevel.LEVEL_5MIN)
    assert is_finished_kdata_timestamp(timestamp, level=IntervalLevel.LEVEL_1MIN)

    timestamp = '2019-01-10'
    assert is_finished_kdata_timestamp(timestamp, level=IntervalLevel.LEVEL_1DAY)


def test_split_time_interval():
    first = None
    last = None
    start = '2020-01-01'
    end = '2021-01-01'
    for interval in split_time_interval(start, end, interval=30):
        if first is None:
            first = interval
        last = interval

    print(first)
    print(last)

    assert is_same_date(first[0], start)
    assert is_same_date(first[-1], '2020-01-31')

    assert is_same_date(last[-1], end)

def test_split_time_interval_month():
    first = None
    last = None
    start = '2020-01-01'
    end = '2021-01-01'
    for interval in split_time_interval(start, end, method='month'):
        if first is None:
            first = interval
        last = interval

    print(first)
    print(last)

    assert is_same_date(first[0], start)
    assert is_same_date(first[-1], '2020-01-31')

    assert is_same_date(last[0], '2021-01-01')
    assert is_same_date(last[-1], '2021-01-01')
