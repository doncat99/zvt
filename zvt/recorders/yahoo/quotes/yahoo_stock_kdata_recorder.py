# -*- coding: utf-8 -*-
import argparse

import pandas as pd

from zvt import init_log
from zvt.api import get_kdata, AdjustType
from zvt.api.quote import generate_kdata_id, get_kdata_schema
from zvt.contract import IntervalLevel
from zvt.contract.api import df_to_db
from zvt.contract.recorder import FixedCycleDataRecorder
from zvt.recorders.joinquant.common import to_yahoo_trading_level
from zvt.domain import Stock, StockKdataCommon, Stock1dKdata
from zvt.utils.pd_utils import pd_is_not_null
from zvt.utils.time_utils import to_time_str, TIME_FORMAT_DAY, TIME_FORMAT_ISO8601
from zvt.utils.request_utils import yh_get_bars


class YahooUsStockKdataRecorder(FixedCycleDataRecorder):
    entity_provider = 'yahoo'
    entity_schema = Stock

    # 数据来自yahoo
    provider = 'yahoo'

    # 只是为了把recorder注册到data_schema
    data_schema = StockKdataCommon

    def __init__(self,
                 exchanges=['NYSE', 'NASDAQ'],
                 entity_ids=None,
                 codes=None,
                 batch_size=10,
                 force_update=True,
                 sleeping_time=0,
                 default_size=2000,
                 real_time=False,
                 fix_duplicate_way='ignore',
                 start_timestamp=None,
                 end_timestamp=None,
                 level=IntervalLevel.LEVEL_1WEEK,
                 kdata_use_begin_time=False,
                 close_hour=15,
                 close_minute=0,
                 one_day_trading_minutes=4 * 60,
                 adjust_type=AdjustType.qfq,
                 share_para=None) -> None:
        level = IntervalLevel(level)
        adjust_type = AdjustType(adjust_type)
        self.data_schema = get_kdata_schema(entity_type='stock', level=level, adjust_type=adjust_type)
        self.yahoo_trading_level = to_yahoo_trading_level(level)

        super().__init__('stock', exchanges, entity_ids, codes, batch_size, force_update, sleeping_time,
                         default_size, real_time, fix_duplicate_way, start_timestamp, end_timestamp, close_hour,
                         close_minute, level, kdata_use_begin_time, one_day_trading_minutes, share_para=share_para)
        self.adjust_type = adjust_type

    def generate_domain_id(self, entity, original_data):
        return generate_kdata_id(entity_id=entity.id, timestamp=original_data['timestamp'], level=self.level)

    # def recompute_qfq(self, entity, qfq_factor, last_timestamp):
    #     # 重新计算前复权数据
    #     if qfq_factor != 0:
    #         kdatas = get_kdata(provider=self.provider, entity_id=entity.id, level=self.level.value,
    #                            order=self.data_schema.timestamp.asc(),
    #                            return_type='domain',
    #                            session=self.session,
    #                            filters=[self.data_schema.timestamp < last_timestamp])
    #         if kdatas:
    #             self.logger.info('recomputing {} qfq kdata,factor is:{}'.format(entity.code, qfq_factor))
    #             for kdata in kdatas:
    #                 kdata.open = round(kdata.open * qfq_factor, 2)
    #                 kdata.close = round(kdata.close * qfq_factor, 2)
    #                 kdata.high = round(kdata.high * qfq_factor, 2)
    #                 kdata.low = round(kdata.low * qfq_factor, 2)
    #             self.session.add_all(kdatas)
    #             self.session.commit()

    def on_finish(self):
        super().on_finish()

    def record(self, entity, start, end, size, timestamps, http_session):
        if not self.end_timestamp:
            df = yh_get_bars(code=entity.code, interval=self.yahoo_trading_level, start=start)
            # df = pdr.get_data_yahoo(entity.code, interval=self.yahoo_trading_level, start=start)
        else:
            end_timestamp = to_time_str(self.end_timestamp)
            df = yh_get_bars(code=entity.code, interval=self.yahoo_trading_level, start=start, end=end_timestamp)
            # df = pdr.get_data_yahoo(entity.code, interval=self.yahoo_trading_level, start=start, end=end_timestamp)

        if pd_is_not_null(df):
            df.reset_index(inplace=True)
            df['name'] = entity.name
            df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', \
                               'Close': 'close','Adj Close': 'adj_close', \
                               'Volume': 'volume', 'Date': 'timestamp'}, inplace=True)

            df['entity_id'] = entity.id
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['provider'] = 'yahoo'
            df['level'] = self.level.value
            df['code'] = entity.code

            # 判断是否需要重新计算之前保存的前复权数据
            # if self.adjust_type == AdjustType.qfq:
            #     check_df = df.head(1)
            #     check_date = check_df['timestamp'][0]
            #     current_df = get_kdata(entity_id=entity.id, provider=self.provider, start_timestamp=check_date,
            #                            end_timestamp=check_date, limit=1, level=self.level,
            #                            adjust_type=self.adjust_type)
            #     if pd_is_not_null(current_df):
            #         old = current_df.iloc[0, :]['close']
            #         new = check_df['close'][0]
            #         # 相同时间的close不同，表明前复权需要重新计算
            #         if round(old, 2) != round(new, 2):
            #             qfq_factor = new / old
            #             last_timestamp = pd.Timestamp(check_date)
            #             self.recompute_qfq(entity, qfq_factor=qfq_factor, last_timestamp=last_timestamp)

            def generate_kdata_id(se):
                if self.level >= IntervalLevel.LEVEL_1DAY:
                    return "{}_{}".format(se['entity_id'], to_time_str(se['timestamp'], fmt=TIME_FORMAT_DAY))
                else:
                    return "{}_{}".format(se['entity_id'], to_time_str(se['timestamp'], fmt=TIME_FORMAT_ISO8601))

            df['id'] = df[['entity_id', 'timestamp']].apply(generate_kdata_id, axis=1)

            df_to_db(df=df, region='us', data_schema=self.data_schema, provider=self.provider, force_update=self.force_update)

        return None


__all__ = ['YahooUsStockKdataRecorder']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', help='trading level', default='1d', choices=[item.value for item in IntervalLevel])
    parser.add_argument('--codes', help='codes', default=['000001'], nargs='+')

    args = parser.parse_args()

    level = IntervalLevel(args.level)
    codes = args.codes

    init_log('yahoo_us_stock_{}_kdata.log'.format(args.level))
    YahooUsStockKdataRecorder(level=level, sleeping_time=0, codes=codes, real_time=False,
                              adjust_type=AdjustType.hfq).run()

    print(get_kdata(entity_id='stock_nyse_a', limit=10, order=Stock1dKdata.timestamp.desc(),
                    adjust_type=AdjustType.hfq))
