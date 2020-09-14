# -*- coding: utf-8 -*-

import pandas as pd
from jqdatasdk import valuation

from zvt.contract.api import df_to_db
from zvt.contract.recorder import TimeSeriesDataRecorder
from zvt.domain import Stock, StockValuation, Etf
from zvt.contract.common import Region, Provider, EntityType
from zvt.recorders.joinquant.common import to_jq_entity_id
from zvt.utils.request_utils import jq_auth, jq_query, jq_get_fundamentals_continuously, jq_logout
from zvt.utils.time_utils import now_pd_timestamp, now_time_str, to_time_str


class JqChinaStockValuationRecorder(TimeSeriesDataRecorder):
    entity_provider = Provider.JoinQuant
    entity_schema = Stock

    # 数据来自jq
    provider = Provider.JoinQuant

    data_schema = StockValuation

    def __init__(self, entity_type=EntityType.Stock, exchanges=None, entity_ids=None, codes=None, batch_size=10,
                 force_update=False, sleeping_time=5, default_size=2000, real_time=False, fix_duplicate_way='add',
                 start_timestamp=None, end_timestamp=None, close_hour=0, close_minute=0, share_para=None) -> None:
        super().__init__(entity_type, exchanges, entity_ids, codes, batch_size, force_update, sleeping_time,
                         default_size, real_time, fix_duplicate_way, start_timestamp, end_timestamp, close_hour,
                         close_minute, share_para=share_para)
        jq_auth()

    def on_finish(self):
        super().on_finish()
        jq_logout()

    def record(self, entity, start, end, size, timestamps, http_session):
        q = jq_query(
            valuation
        ).filter(
            valuation.code == to_jq_entity_id(entity)
        )
        count: pd.Timedelta = now_pd_timestamp(Region.CHN) - start
        df = jq_get_fundamentals_continuously(q, end_date=now_time_str(Region.CHN), count=count.days + 1, panel=False)
        df['entity_id'] = entity.id
        df['timestamp'] = pd.to_datetime(df['day'])
        df['code'] = entity.code
        df['name'] = entity.name
        df['id'] = df['timestamp'].apply(lambda x: "{}_{}".format(entity.id, to_time_str(x)))
        df = df.rename({'pe_ratio_lyr': 'pe',
                        'pe_ratio': 'pe_ttm',
                        'pb_ratio': 'pb',
                        'ps_ratio': 'ps',
                        'pcf_ratio': 'pcf'},
                       axis='columns')

        df['market_cap'] = df['market_cap'] * 100000000
        df['circulating_market_cap'] = df['circulating_market_cap'] * 100000000
        df['capitalization'] = df['capitalization'] * 10000
        df['circulating_cap'] = df['circulating_cap'] * 10000
        df['turnover_ratio'] = df['turnover_ratio'] * 0.01
        df_to_db(df=df, region=Region.CHN, data_schema=self.data_schema, provider=self.provider, force_update=self.force_update)

        return None


__all__ = ['JqChinaStockValuationRecorder']

if __name__ == '__main__':
    # 上证50
    df = Etf.get_stocks(timestamp=now_pd_timestamp(Region.CHN), code='510050')
    stocks = df.stock_id.tolist()
    print(stocks)
    print(len(stocks))

    JqChinaStockValuationRecorder(entity_ids=stocks, force_update=True).run()
