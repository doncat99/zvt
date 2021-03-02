# -*- coding: utf-8 -*-
from typing import List, Union

import pandas as pd

from zvt.api.data_type import Region, Provider
from zvt.domain import Stock, Stock1dKdata
from zvt.contract import IntervalLevel, EntityMixin, AdjustType
from zvt.contract.drawer import Drawer
from zvt.contract.factor import Accumulator, Transformer
from zvt.contract.reader import DataReader
from zvt.factors.technical_factor import TechnicalFactor
from zvt.utils.time_utils import now_pd_timestamp


class TopBottomTransformer(Transformer):
    def __init__(self, window=20) -> None:
        super().__init__()
        self.window = window

    def transform(self, input_df) -> pd.DataFrame:
        top_df = input_df['high'].groupby(level=0).rolling(window=self.window, min_periods=self.window).max()
        top_df = top_df.reset_index(level=0, drop=True)
        input_df['top'] = top_df

        bottom_df = input_df['high'].groupby(level=0).rolling(window=self.window, min_periods=self.window).min()
        bottom_df = bottom_df.reset_index(level=0, drop=True)
        input_df['bottom'] = bottom_df

        return input_df


class TopBottomFactor(TechnicalFactor):
    def __init__(self, region: Region, entity_schema: EntityMixin = Stock, 
                 provider: Provider = Provider.Default,
                 entity_ids: List[str] = None,
                 exchanges: List[str] = None, codes: List[str] = None,
                 the_timestamp: Union[str, pd.Timestamp] = None, start_timestamp: Union[str, pd.Timestamp] = None,
                 end_timestamp: Union[str, pd.Timestamp] = None,
                 columns: List = ['id', 'entity_id', 'timestamp', 'level', 'open', 'close', 'high', 'low'],
                 filters: List = None, order: object = None, limit: int = None,
                 level: Union[str, IntervalLevel] = IntervalLevel.LEVEL_1DAY, category_field: str = 'entity_id',
                 time_field: str = 'timestamp', computing_window: int = None, keep_all_timestamp: bool = False,
                 fill_method: str = 'ffill', effective_number: int = None,
                 accumulator: Accumulator = None, need_persist: bool = False, dry_run: bool = False,
                 factor_name: str = None, clear_state: bool = False, not_load_data: bool = False,
                 adjust_type: Union[AdjustType, str] = None, window=30) -> None:
        self.adjust_type = adjust_type

        transformer = TopBottomTransformer(window=window)

        super().__init__(region, entity_schema, provider, entity_ids, exchanges, codes, the_timestamp,
                         start_timestamp, end_timestamp, columns, filters, order, limit, level, category_field,
                         time_field, computing_window, keep_all_timestamp, fill_method, effective_number, transformer,
                         accumulator, need_persist, dry_run, factor_name, clear_state, not_load_data, adjust_type)


if __name__ == '__main__':
    factor = TopBottomFactor(codes=['601318'], start_timestamp='2005-01-01',
                             end_timestamp=now_pd_timestamp(Region.CHN),
                             level=IntervalLevel.LEVEL_1DAY, window=120)
    print(factor.factor_df)

    data_reader1 = DataReader(region=Region.CHN, codes=['601318'],
                              data_schema=Stock1dKdata, entity_schema=Stock)

    drawer = Drawer(main_df=data_reader1.data_df, factor_df_list=[factor.factor_df[['top', 'bottom']]])
    drawer.draw_kline(show=True)


# the __all__ is generated
__all__ = ['TopBottomTransformer', 'TopBottomFactor']
