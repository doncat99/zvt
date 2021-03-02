# -*- coding: utf-8 -*-
from typing import List, Union

import pandas as pd

from zvt.api.data_type import Region, Provider
from zvt.api.normal_data import NormalData
from zvt.domain import AccountStats, Order, trader_info
from zvt.contract import IntervalLevel
from zvt.contract.api import get_data, get_db_session
from zvt.contract.reader import DataReader
from zvt.contract.drawer import Drawer


def get_trader_info(region: Region, trader_name=None, return_type='df', start_timestamp=None, end_timestamp=None,
                    filters=None, session=None, order=None, limit=None) -> List[trader_info.TraderInfo]:
    if trader_name:
        if filters:
            filters = filters + [trader_info.TraderInfo.trader_name == trader_name]
        else:
            filters = [trader_info.TraderInfo.trader_name == trader_name]

    return get_data(data_schema=trader_info.TraderInfo, region=region, entity_id=None, codes=None, level=None, provider=Provider.ZVT,
                    columns=None, return_type=return_type, start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp, filters=filters, session=session, order=order, limit=limit)


def get_order_securities(trader_name):
    items = get_db_session(region=Region.CHN, provider=Provider.ZVT, data_schema=Order).query(Order.entity_id).filter(
        Order.trader_name == trader_name).group_by(Order.entity_id).all()

    return [item[0] for item in items]


class AccountStatsReader(DataReader):
    def __init__(self,
                 region: Region,
                 the_timestamp: Union[str, pd.Timestamp] = None,
                 start_timestamp: Union[str, pd.Timestamp] = None,
                 end_timestamp: Union[str, pd.Timestamp] = None,
                 columns: List = None,
                 filters: List = None,
                 order: object = None,
                 level: IntervalLevel = IntervalLevel.LEVEL_1DAY,
                 trader_names: List[str] = None) -> None:
        self.trader_names = trader_names

        self.filters = filters

        if self.trader_names:
            filter = [AccountStats.trader_name == name for name in self.trader_names]
            if self.filters:
                self.filters += filter
            else:
                self.filters = filter
        super().__init__(region, AccountStats, None, None, None, None, None, None,
                         the_timestamp, start_timestamp, end_timestamp, columns, self.filters, order, None, level,
                         category_field='trader_name', time_field='timestamp', computing_window=None)

    def draw_line(self, show=True):
        drawer = Drawer(main_data=NormalData(self.data_df.copy()[['trader_name', 'timestamp', 'all_value']],
                                             category_field='trader_name'))
        return drawer.draw_line(show=show)


class OrderReader(DataReader):
    def __init__(self,
                 region: Region,
                 the_timestamp: Union[str, pd.Timestamp] = None,
                 start_timestamp: Union[str, pd.Timestamp] = None,
                 end_timestamp: Union[str, pd.Timestamp] = None,
                 columns: List = None,
                 filters: List = None,
                 order: object = None,
                 level: IntervalLevel = None,
                 trader_names: List[str] = None) -> None:
        self.trader_names = trader_names

        self.filters = filters

        if self.trader_names:
            filter = [Order.trader_name == name for name in self.trader_names]
            if self.filters:
                self.filters += filter
            else:
                self.filters = filter

        super().__init__(region, Order, None, None, None, None, None, None,
                         the_timestamp, start_timestamp, end_timestamp, columns, self.filters, order, None, level,
                         category_field='trader_name', time_field='timestamp', computing_window=None)


if __name__ == '__main__':
    reader = AccountStatsReader(region=Region.CHN, trader_names=['000338_ma_trader'])
    drawer = Drawer(main_data=NormalData(reader.data_df.copy()[['trader_name', 'timestamp', 'all_value']],
                                         category_field='trader_name'))
    drawer.draw_line()
# the __all__ is generated
__all__ = ['get_trader_info', 'get_order_securities', 'AccountStatsReader', 'OrderReader']
