# -*- coding: utf-8 -*-
from datetime import datetime

import pandas as pd
import numpy as np

from zvt.api.data_type import Region, Provider
from zvt.domain import SpoDetail, DividendFinancing
from zvt.contract.api import get_db_session
from zvt.recorders.eastmoney.common import EastmoneyPageabeDataRecorder
from zvt.utils.pd_utils import pd_is_not_null
from zvt.utils.time_utils import now_pd_timestamp
from zvt.utils.utils import to_float


class SPODetailRecorder(EastmoneyPageabeDataRecorder):
    data_schema = SpoDetail

    region = Region.CHN
    provider = Provider.EastMoney

    url = 'https://emh5.eastmoney.com/api/FenHongRongZi/GetZengFaMingXiList'
    page_url = url
    path_fields = ['ZengFaMingXiList']

    def get_original_time_field(self):
        return 'ZengFaShiJian'

    def format(self, entity, df):
        df['spo_issues'] = df['ShiJiZengFa'].apply(lambda x: to_float(x))
        df['spo_price'] = df['ZengFaJiaGe'].apply(lambda x: to_float(x))
        df['spo_raising_fund'] = df['ShiJiMuJi'].apply(lambda x: to_float(x))

        df.update(df.select_dtypes(include=[np.number]).fillna(0))

        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.to_datetime(df[self.get_original_time_field()])
        elif not isinstance(df['timestamp'].dtypes, datetime):
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        df['entity_id'] = entity.id
        df['provider'] = self.provider.value
        df['code'] = entity.code

        df['id'] = self.generate_domain_id(entity, df)
        return df

    def on_finish(self):
        last_year = str(now_pd_timestamp(Region.CHN).year)
        codes = [item.code for item in self.entities]
        need_filleds = DividendFinancing.query_data(region=self.region,
                                                    provider=self.provider,
                                                    codes=codes,
                                                    return_type='domain',
                                                    filters=[DividendFinancing.spo_raising_fund.is_(None)],
                                                    end_timestamp=last_year)

        for item in need_filleds:
            df = SpoDetail.query_data(region=self.region,
                                      provider=self.provider,
                                      entity_id=item.entity_id,
                                      columns=[SpoDetail.id, SpoDetail.timestamp, SpoDetail.spo_raising_fund],
                                      start_timestamp=item.timestamp,
                                      end_timestamp="{}-12-31".format(item.timestamp.year))
            if pd_is_not_null(df):
                item.spo_raising_fund = df['spo_raising_fund'].sum()
                session = get_db_session(region=self.region,
                                         provider=self.provider,
                                         data_schema=self.data_schema)
                session.commit()
        super().on_finish()


__all__ = ['SPODetailRecorder']

if __name__ == '__main__':
    # init_log('spo_detail.log')

    recorder = SPODetailRecorder(codes=['000999'])
    recorder.run()
