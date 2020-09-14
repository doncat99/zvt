# -*- coding: utf-8 -*-
import pandas as pd
from jqdatasdk import indicator

from zvt.api.quote import to_jq_report_period
from zvt.contract.api import get_data
from zvt.contract.common import EntityType
from zvt.domain import FinanceFactor
from zvt.recorders.eastmoney.common import company_type_flag, get_fc, EastmoneyTimestampsDataRecorder, \
                                           call_eastmoney_api, get_from_path_fields
from zvt.recorders.joinquant.common import to_jq_entity_id
from zvt.utils.pd_utils import index_df
from zvt.utils.pd_utils import pd_is_not_null
from zvt.utils.time_utils import to_time_str, to_pd_timestamp
from zvt.utils.request_utils import jq_auth, jq_query, jq_get_fundamentals, jq_logout


class BaseChinaStockFinanceRecorder(EastmoneyTimestampsDataRecorder):
    finance_report_type = None
    data_type = 1

    timestamps_fetching_url = 'https://emh5.eastmoney.com/api/CaiWuFenXi/GetCompanyReportDateList'
    timestamp_list_path_fields = ['CompanyReportDateList']
    timestamp_path_fields = ['ReportDate']

    def __init__(self, entity_type=EntityType.Stock, exchanges=['sh', 'sz'], 
                 entity_ids=None, codes=None, batch_size=10,
                 force_update=False, sleeping_time=5, default_size=2000, real_time=False,
                 fix_duplicate_way='add', start_timestamp=None, end_timestamp=None, close_hour=0,
                 close_minute=0, share_para=None) -> None:
        super().__init__(entity_type, exchanges, entity_ids, codes, batch_size, force_update, 
                         sleeping_time, default_size, real_time, fix_duplicate_way, start_timestamp, 
                         end_timestamp, close_hour, close_minute, share_para=share_para)
        self.fetch_jq_timestamp = jq_auth()
            
    def init_timestamps(self, entity, http_session):
        param = {
            "color": "w",
            "fc": get_fc(entity),
            "DataType": self.data_type
        }

        if self.finance_report_type == 'LiRunBiaoList' or self.finance_report_type == 'XianJinLiuLiangBiaoList':
            param['ReportType'] = 1

        timestamp_json_list = call_eastmoney_api(http_session,
                                                 url=self.timestamps_fetching_url,
                                                 path_fields=self.timestamp_list_path_fields,
                                                 param=param)

        if timestamp_json_list is not None and self.timestamp_path_fields:
            timestamps = [get_from_path_fields(data, self.timestamp_path_fields) for data in timestamp_json_list]
        else:
            return []

        return [to_pd_timestamp(t) for t in timestamps]

    def generate_request_param(self, security_item, start, end, size, timestamps, http_session):
        if len(timestamps) <= 10:
            param = {
                "color": "w",
                "fc": get_fc(security_item),
                "corpType": company_type_flag(security_item, http_session),
                # 0 means get all types
                "reportDateType": 0,
                "endDate": '',
                "latestCount": size
            }
        else:
            param = {
                "color": "w",
                "fc": get_fc(security_item),
                "corpType": company_type_flag(security_item, http_session),
                # 0 means get all types
                "reportDateType": 0,
                "endDate": to_time_str(timestamps[10]),
                "latestCount": 10
            }

        if self.finance_report_type == 'LiRunBiaoList' or self.finance_report_type == 'XianJinLiuLiangBiaoList':
            param['reportType'] = 1

        return param

    def generate_path_fields(self, security_item, http_session):
        comp_type = company_type_flag(security_item, http_session)

        if comp_type == "3":
            return ['{}_YinHang'.format(self.finance_report_type)]
        elif comp_type == "2":
            return ['{}_BaoXian'.format(self.finance_report_type)]
        elif comp_type == "1":
            return ['{}_QuanShang'.format(self.finance_report_type)]
        elif comp_type == "4":
            return ['{}_QiYe'.format(self.finance_report_type)]

    def record(self, entity, start, end, size, timestamps, http_session):
        # different with the default timestamps handling
        param = self.generate_request_param(entity, start, end, size, timestamps, http_session)
        # self.logger.info('request param:{}'.format(param))

        return self.api_wrapper.request(http_session=http_session, url=self.url, param=param, method=self.request_method,
                                        path_fields=self.generate_path_fields(entity, http_session))

    def get_original_time_field(self):
        return 'ReportDate'

    def fill_timestamp_with_jq(self, security_item, the_data):
        # get report published date from jq
        try:
            q = jq_query(
                indicator.pubDate
            ).filter(
                indicator.code == to_jq_entity_id(security_item),
            )

            df = jq_get_fundamentals(q, statDate=to_jq_report_period(the_data.report_date))
            if pd_is_not_null(df) and pd.isna(df).empty:
                the_data.timestamp = to_pd_timestamp(df['pubDate'][0])
                self.logger.info(
                    'jq fill {} {} timestamp:{} for report_date:{}'.format(self.data_schema, security_item.id,
                                                                           the_data.timestamp,
                                                                           the_data.report_date))
                self.session.commit()
        except Exception as e:
            self.logger.error(e)

    def on_finish_entity(self, entity, http_session):
        super().on_finish_entity(entity, http_session)

        if not self.fetch_jq_timestamp:
            return

        # fill the timestamp for report published date
        the_data_list = get_data(data_schema=self.data_schema,
                                 provider=self.provider,
                                 entity_id=entity.id,
                                 order=self.data_schema.timestamp.asc(),
                                 return_type='domain',
                                 session=self.session,
                                 filters=[self.data_schema.timestamp != self.data_schema.report_date,
                                          self.data_schema.timestamp >= to_pd_timestamp('2005-01-01')])
        if the_data_list:
            if self.data_schema == FinanceFactor:
                for the_data in the_data_list:
                    self.fill_timestamp_with_jq(entity, the_data)
            else:
                df = FinanceFactor.query_data(entity_id=entity.id,
                                              columns=[FinanceFactor.timestamp, FinanceFactor.report_date,
                                                       FinanceFactor.id],
                                              filters=[FinanceFactor.timestamp != FinanceFactor.report_date,
                                                       FinanceFactor.timestamp >= to_pd_timestamp('2005-01-01'),
                                                       FinanceFactor.report_date >= the_data_list[0].report_date,
                                                       FinanceFactor.report_date <= the_data_list[-1].report_date, ])

                if pd_is_not_null(df):
                    index_df(df, index='report_date', time_field='report_date')

                for the_data in the_data_list:
                    if pd_is_not_null(df) and the_data.report_date in df.index:
                        the_data.timestamp = df.at[the_data.report_date, 'timestamp']
                        self.logger.info(
                            'db fill {} {} timestamp:{} for report_date:{}'.format(self.data_schema, entity.id,
                                                                                   the_data.timestamp,
                                                                                   the_data.report_date))
                        self.session.commit()
                    else:
                        # self.logger.info(
                        #     'waiting jq fill {} {} timestamp:{} for report_date:{}'.format(self.data_schema,
                        #                                                                    security_item.id,
                        #                                                                    the_data.timestamp,
                        #                                                                    the_data.report_date))

                        self.fill_timestamp_with_jq(entity, the_data)

    def on_finish(self):
        super().on_finish()
        jq_logout()
