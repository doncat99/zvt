from jqdatasdk import finance

from zvt.contract.recorder import TimeSeriesDataRecorder
from zvt.contract.common import Provider
from zvt.utils.time_utils import to_time_str
from zvt.utils.request_utils import jq_auth, jq_query
from zvt.domain import Index, MarginTradingSummary

# 聚宽编码
# XSHG-上海证券交易所
# XSHE-深圳证券交易所

code_map_jq = {
    '000001': 'XSHG',
    '399106': 'XSHE'
}


class MarginTradingSummaryRecorder(TimeSeriesDataRecorder):
    entity_provider = Provider.Exchange
    entity_schema = Index

    provider = Provider.JoinQuant
    data_schema = MarginTradingSummary

    def __init__(self, batch_size=10,
                 force_update=False, sleeping_time=5, default_size=2000, real_time=False,
                 fix_duplicate_way='add', share_para=None) -> None:
        # 上海A股,深圳市场
        codes = ['000001', '399106']
        super().__init__('index', ['cn'], None, codes, batch_size,
                         force_update, sleeping_time,
                         default_size, real_time, fix_duplicate_way, share_para=share_para)
        jq_auth()

    def record(self, entity, start, end, size, timestamps, http_session):
        jq_code = code_map_jq.get(entity.code)

        q = jq_query(finance.STK_MT_TOTAL).filter(
                finance.STK_MT_TOTAL.exchange_code == jq_code,
                finance.STK_MT_TOTAL.date >= to_time_str(start)).limit(2000)

        df = finance.run_query(q)

        json_results = []

        for item in df.to_dict(orient='records'):
            result = {
                'provider': self.provider.value,
                'timestamp': item['date'],
                'name': entity.name,
                'margin_value': item['fin_value'],
                'margin_buy': item['fin_buy_value'],
                'short_value': item['sec_value'],
                'short_volume': item['sec_sell_volume'],
                'total_value': item['fin_sec_value']
            }

            json_results.append(result)

        if len(json_results) < 100:
            self.one_shot = True

        return json_results

    def get_data_map(self):
        return None


__all__ = ['MarginTradingSummaryRecorder']

if __name__ == '__main__':
    MarginTradingSummaryRecorder(batch_size=30).run()
