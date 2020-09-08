from jqdatasdk import finance

from zvt.contract.recorder import TimeSeriesDataRecorder
from zvt.contract.common import Provider
from zvt.utils.time_utils import to_time_str
from zvt.utils.utils import multiple_number
from zvt.utils.request_utils import jq_auth, jq_query
from zvt.domain import Index
from zvt.domain import StockSummary

# 聚宽编码
# 322001	上海市场
# 322002	上海A股
# 322003	上海B股
# 322004	深圳市场	该市场交易所未公布成交量和成交笔数
# 322005	深市主板
# 322006	中小企业板
# 322007	创业板

code_map_jq = {
    '000001': '322002',
    '399106': '322004',
    '399001': '322005',
    '399005': '322006',
    '399006': '322007'
}


class StockSummaryRecorder(TimeSeriesDataRecorder):
    entity_provider = Provider.Exchange
    entity_schema = Index

    provider = Provider.JoinQuant
    data_schema = StockSummary

    def __init__(self, batch_size=10,
                 force_update=False, sleeping_time=5, default_size=2000, real_time=False,
                 fix_duplicate_way='add', share_para=None) -> None:
        # 上海A股,深圳市场,深圳成指,中小板,创业板
        codes = ['000001', '399106', '399001', '399005', '399006']
        super().__init__('index', ['cn'], None, codes, batch_size,
                         force_update, sleeping_time,
                         default_size, real_time, fix_duplicate_way, share_para=share_para)
        jq_auth()

    def record(self, entity, start, end, size, timestamps, http_session):
        jq_code = code_map_jq.get(entity.code)

        q = jq_query(finance.STK_EXCHANGE_TRADE_INFO).filter(
                finance.STK_EXCHANGE_TRADE_INFO.exchange_code == jq_code,
                finance.STK_EXCHANGE_TRADE_INFO.date >= to_time_str(start)).limit(2000)

        df = finance.run_query(q)

        json_results = []

        for item in df.to_dict(orient='records'):
            result = {
                'provider': self.provider.value,
                'timestamp': item['date'],
                'name': entity.name,
                'pe': item['pe_average'],
                'total_value': multiple_number(item['total_market_cap'], 100000000),
                'total_tradable_vaule': multiple_number(item['circulating_market_cap'], 100000000),
                'volume': multiple_number(item['volume'], 10000),
                'turnover': multiple_number(item['money'], 100000000),
                'turnover_rate': item['turnover_ratio']
            }

            json_results.append(result)

        if len(json_results) < 100:
            self.one_shot = True

        return json_results

    def get_data_map(self):
        return None


__all__ = ['StockSummaryRecorder']

if __name__ == '__main__':
    StockSummaryRecorder(batch_size=30).run()
