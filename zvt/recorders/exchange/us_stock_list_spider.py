# -*- coding: utf-8 -*-

import io

import pandas as pd

from zvt.contract.api import df_to_db
from zvt.contract.recorder import Recorder
from zvt.utils.time_utils import to_pd_timestamp
from zvt.utils.request_utils import get_http_session, request_get
from zvt.domain import Stock, StockDetail
from zvt.recorders.consts import DEFAULT_SH_HEADER, DEFAULT_SZ_HEADER


class ExchangeUsStockListRecorder(Recorder):
    data_schema = Stock
    provider = 'exchange'

    def run(self):
        http_session = get_http_session()

        exchanges = ['NYSE', 'NASDAQ', 'AMEX']

        for exchange in exchanges:
            url = 'https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&render=download&exchange={}'.format(exchange)
            resp = request_get(http_session, url)
            self.download_stock_list(response=resp, exchange=exchange)


    def download_stock_list(self, response, exchange):
        df = pd.read_csv(io.BytesIO(response.content), encoding='UTF8', dtype=str)

        print("exchange:", exchange)
        print(df)

        # if df is not None:
        #     df.columns = ['code', 'name', 'list_date']

        #     df = df.dropna(subset=['code'])

        #     df['list_date'] = df['list_date'].apply(lambda x: to_pd_timestamp(x))
        #     df['exchange'] = exchange
        #     df['entity_type'] = 'stock'
        #     df['id'] = df[['entity_type', 'exchange', 'code']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
        #     df['entity_id'] = df['id']
        #     df['timestamp'] = df['list_date']
        #     df = df.dropna(axis=0, how='any')
        #     df = df.drop_duplicates(subset=('id'), keep='last')
        #     df_to_db(df=df, data_schema=self.data_schema, provider=self.provider, force_update=False)
        #     # persist StockDetail too
        #     df_to_db(df=df, data_schema=StockDetail, provider=self.provider, force_update=False)
        #     # self.logger.info(df.tail())
        #     self.logger.info("persist stock list successs")


__all__ = ['ExchangeUsStockListRecorder']

if __name__ == '__main__':
    spider = ExchangeUsStockListRecorder()
    spider.run()
