# -*- coding: utf-8 -*-
import pandas as pd
from jqdatasdk import finance

from zvt.contract.api import df_to_db, get_entity_exchange, get_entity_code
from zvt.contract.recorder import Recorder, TimeSeriesDataRecorder
from zvt.api.quote import china_stock_code_to_id, portfolio_relate_stock
from zvt.domain import EtfStock, Stock, Etf, StockDetail
from zvt.contract.common import Region, Provider, EntityType
from zvt.recorders.joinquant.common import to_entity_id, jq_to_report_period
from zvt.utils.pd_utils import pd_is_not_null
from zvt.utils.request_utils import jq_auth, jq_get_all_securities, jq_query, jq_logout


class BaseJqChinaMetaRecorder(Recorder):
    provider = Provider.JoinQuant

    def __init__(self, batch_size=10, force_update=True, sleeping_time=10, share_para=None) -> None:
        super().__init__(batch_size, force_update, sleeping_time)
        jq_auth()

    def to_zvt_entity(self, df, entity_type: EntityType, category=None):
        df.index.name = 'entity_id'
        df = df.reset_index()
        # 上市日期
        df.rename(columns={'start_date': 'timestamp'}, inplace=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['list_date'] = df['timestamp']
        df['end_date'] = pd.to_datetime(df['end_date'])

        df['entity_id'] = df['entity_id'].apply(lambda x: to_entity_id(entity_type=entity_type, jq_code=x))
        df['id'] = df['entity_id']
        df['entity_type'] = entity_type.value
        df['exchange'] = df['entity_id'].apply(lambda x: get_entity_exchange(x))
        df['code'] = df['entity_id'].apply(lambda x: get_entity_code(x))
        df['name'] = df['display_name']

        if category:
            df['category'] = category

        return df


class JqChinaStockRecorder(BaseJqChinaMetaRecorder):
    data_schema = Stock

    def run(self):
        # 抓取股票列表
        df_stock = self.to_zvt_entity(jq_get_all_securities(['stock']), entity_type=EntityType.Stock)
        df_to_db(df_stock, region=Region.CHN, data_schema=Stock, provider=self.provider, force_update=self.force_update)
        # persist StockDetail too
        df_to_db(df=df_stock, region=Region.CHN, data_schema=StockDetail, provider=self.provider, force_update=self.force_update)

        # self.logger.info(df_stock)
        self.logger.info("persist stock list success")

        jq_logout()


class JqChinaEtfRecorder(BaseJqChinaMetaRecorder):
    data_schema = Etf

    def run(self):
        # 抓取etf列表
        df_index = self.to_zvt_entity(jq_get_all_securities(['etf']), entity_type=EntityType.ETF, category='etf')
        df_to_db(df_index, region=Region.CHN, data_schema=Etf, provider=self.provider, force_update=self.force_update)

        # self.logger.info(df_index)
        self.logger.info("persist etf list success")
        jq_logout()


class JqChinaStockEtfPortfolioRecorder(TimeSeriesDataRecorder):
    entity_provider = Provider.JoinQuant
    entity_schema = Etf

    # 数据来自jq
    provider = Provider.JoinQuant

    data_schema = EtfStock

    def __init__(self, entity_type=EntityType.ETF, exchanges=['sh', 'sz'], entity_ids=None, codes=None, batch_size=10,
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
        q = jq_query(finance.FUND_PORTFOLIO_STOCK).filter(finance.FUND_PORTFOLIO_STOCK.pub_date >= start).filter(
            finance.FUND_PORTFOLIO_STOCK.code == entity.code)
        df = finance.run_query(q)
        if pd_is_not_null(df):
            #          id    code period_start  period_end    pub_date  report_type_id report_type  rank  symbol  name      shares    market_cap  proportion
            # 0   8640569  159919   2018-07-01  2018-09-30  2018-10-26          403003        第三季度     1  601318  中国平安  19869239.0  1.361043e+09        7.09
            # 1   8640570  159919   2018-07-01  2018-09-30  2018-10-26          403003        第三季度     2  600519  贵州茅台    921670.0  6.728191e+08        3.50
            # 2   8640571  159919   2018-07-01  2018-09-30  2018-10-26          403003        第三季度     3  600036  招商银行  18918815.0  5.806184e+08        3.02
            # 3   8640572  159919   2018-07-01  2018-09-30  2018-10-26          403003        第三季度     4  601166  兴业银行  22862332.0  3.646542e+08        1.90
            df['timestamp'] = pd.to_datetime(df['pub_date'])

            df.rename(columns={'symbol': 'stock_code', 'name': 'stock_name'}, inplace=True)
            df['proportion'] = df['proportion'] * 0.01

            df = portfolio_relate_stock(df, entity)

            df['stock_id'] = df['stock_code'].apply(lambda x: china_stock_code_to_id(x))
            df['id'] = df[['entity_id', 'stock_id', 'pub_date', 'id']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
            df['report_date'] = pd.to_datetime(df['period_end'])
            df['report_period'] = df['report_type'].apply(lambda x: jq_to_report_period(x))

            df_to_db(df=df, region=Region.CHN, data_schema=self.data_schema, provider=self.provider, force_update=self.force_update)

            # self.logger.info(df.tail())
            self.logger.info(f"persist etf {entity.code} portfolio success")

        return None


__all__ = ['JqChinaStockRecorder', 'JqChinaEtfRecorder', 'JqChinaStockEtfPortfolioRecorder']

if __name__ == '__main__':
    # JqChinaStockRecorder().run()
    JqChinaStockEtfPortfolioRecorder(codes=['510050']).run()
