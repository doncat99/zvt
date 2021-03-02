# -*- coding: utf-8 -*-
import enum
import itertools
from typing import Union

import pandas as pd

from zvt.api.data_type import Region, EntityType
from zvt.api.quote import get_kdata_schema, get_recent_report_date
from zvt.contract import Mixin, AdjustType
from zvt.contract.api import decode_entity_id
from zvt.domain import FundStock
from zvt.utils.time_utils import now_pd_timestamp


class WindowMethod(enum.Enum):
    change = 'change'
    avg = 'avg'
    sum = 'sum'


class TopType(enum.Enum):
    positive = 'positive'
    negative = 'negative'


def get_top_performance_entities(entity_type=EntityType.Stock, start_timestamp=None, end_timestamp=None, pct=0.1,
                                 return_type=None, adjust_type: Union[AdjustType, str] = None):
    if not adjust_type and entity_type == EntityType.Stock:
        adjust_type = AdjustType.hfq
    data_schema = get_kdata_schema(entity_type=entity_type, adjust_type=adjust_type)

    return get_top_entities(data_schema=data_schema, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                            column='close', pct=pct, method=WindowMethod.change, return_type=return_type)


def get_top_fund_holding_stocks(timestamp=None, pct=0.3):
    if not timestamp:
        timestamp = now_pd_timestamp()
    # 季报一般在report_date后1个月内公布，年报2个月内，年报4个月内
    # 所以取时间点的最近的两个公布点，保证取到数据
    # 所以，这是个滞后的数据，只是为了看个大概，毕竟模糊的正确better than 精确的错误
    report_date = get_recent_report_date(timestamp, 1)
    df = FundStock.query_data(region=Region.CHN, filters=[FundStock.report_date >= report_date, FundStock.timestamp <= timestamp])
    g = df.groupby('stock_id')
    market = g['market_cap'].sum().sort_values(ascending=False)
    s = market.iloc[:int(len(market) * pct)]

    return s.to_frame()


def get_performance(region: Region, entity_ids, start_timestamp=None, end_timestamp=None, adjust_type: Union[AdjustType, str] = None):
    entity_type, _, _ = decode_entity_id(entity_ids[0])
    if not adjust_type and entity_type == EntityType.Stock:
        adjust_type = AdjustType.hfq
    data_schema = get_kdata_schema(entity_type=entity_type, adjust_type=adjust_type)

    result, _ = get_top_entities(region=region, data_schema=data_schema, column='close', start_timestamp=start_timestamp,
                                 end_timestamp=end_timestamp, pct=1, method=WindowMethod.change,
                                 return_type=TopType.positive, filters=[data_schema.entity_id.in_(entity_ids)])
    return result


def get_top_volume_entities(region: Region, entity_type=EntityType.Stock, entity_ids=None, start_timestamp=None, end_timestamp=None, pct=0.1,
                            return_type=TopType.positive, adjust_type: Union[AdjustType, str] = None,
                            method=WindowMethod.avg):
    if not adjust_type and entity_type == EntityType.Stock:
        adjust_type = AdjustType.hfq
    data_schema = get_kdata_schema(entity_type=entity_type, adjust_type=adjust_type)

    filters = None
    if entity_ids:
        filters = [data_schema.entity_id.in_(entity_ids)]

    result, _ = get_top_entities(region=region, data_schema=data_schema, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                                 column='turnover', pct=pct, method=method, return_type=return_type, filters=filters)
    return result


def get_top_entities(region: Region, data_schema: Mixin, column: str, start_timestamp=None, end_timestamp=None, pct=0.1,
                     method: WindowMethod = WindowMethod.change,
                     return_type: TopType = None, filters=None):
    """
    get top entities in specific domain between time range

    :param data_schema: schema in domain
    :param column: schema column
    :param start_timestamp:
    :param end_timestamp:
    :param pct: range (0,1]
    :param method:
    :param return_type:
    :param filters:
    :return:
    """
    if type(method) == str:
        method = WindowMethod(method)

    if type(return_type) == str:
        return_type = TopType(return_type)

    all_df = data_schema.query_data(region=region, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                                    columns=['entity_id', column], filters=filters)
    g = all_df.groupby('entity_id')
    tops = {}
    for entity_id, df in g:
        if method == WindowMethod.change:
            start = df[column].iloc[0]
            end = df[column].iloc[-1]
            change = (end - start) / start
            tops[entity_id] = change
        elif method == WindowMethod.avg:
            tops[entity_id] = df[column].mean()
        elif method == WindowMethod.sum:
            tops[entity_id] = df[column].sum()

    positive_df = None
    negative_df = None
    top_index = int(len(tops) * pct)
    if return_type is None or return_type == TopType.positive:
        # from big to small
        positive_tops = {k: v for k, v in sorted(tops.items(), key=lambda item: item[1], reverse=True)}
        positive_tops = dict(itertools.islice(positive_tops.items(), top_index))
        positive_df = pd.DataFrame.from_dict(positive_tops, orient='index')

        col = 'score'
        positive_df.columns = [col]
        positive_df.sort_values(by=col, ascending=False)
    if return_type is None or return_type == TopType.negative:
        # from small to big
        negative_tops = {k: v for k, v in sorted(tops.items(), key=lambda item: item[1])}
        negative_tops = dict(itertools.islice(negative_tops.items(), top_index))
        negative_df = pd.DataFrame.from_dict(negative_tops, orient='index')

        col = 'score'
        negative_df.columns = [col]
        negative_df.sort_values(by=col)

    return positive_df, negative_df


if __name__ == '__main__':
    from pprint import pprint

    tops1, tops2 = get_top_performance_entities(region=Region.CHN, start_timestamp='2020-01-01')

    pprint(tops1)
    pprint(tops2)
# the __all__ is generated
__all__ = ['get_top_performance_entities', 'get_performance', 'get_top_volume_entities', 'get_top_entities']
