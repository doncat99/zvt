# -*- coding: utf-8 -*-
from sqlalchemy import String, Column, Float

from zvt.contract import Mixin


class KdataCommon(Mixin):
    provider = Column(String(length=32))
    code = Column(String(length=32))
    name = Column(String(length=128))
    # Enum constraint is not extendable
    # level = Column(Enum(IntervalLevel, values_callable=enum_value))
    level = Column(String(length=32))

    # 如果是股票，代表前复权数据
    # 开盘价
    open = Column(Float)
    # 收盘价
    close = Column(Float)
    # 调整收盘价
    adj_close = Column(Float)
    # 最高价
    high = Column(Float)
    # 最低价
    low = Column(Float)
    # 成交量
    volume = Column(Float)
    # 成交金额
    turnover = Column(Float)


class TickCommon(Mixin):
    provider = Column(String(length=32))
    code = Column(String(length=32))
    name = Column(String(length=128))
    level = Column(String(length=32))

    order = Column(String(length=32))
    price = Column(Float)
    volume = Column(Float)
    turnover = Column(Float)
    direction = Column(String(length=32))
    order_type = Column(String(length=32))


class BlockKdataCommon(KdataCommon):
    pass


class IndexKdataCommon(KdataCommon):
    pass


class EtfKdataCommon(KdataCommon):
    turnover_rate = Column(Float)

    # ETF 累计净值（货币 ETF 为七日年化)
    cumulative_net_value = Column(Float)
    # ETF 净值增长率
    change_pct = Column(Float)


class StockKdataCommon(KdataCommon):
    # 涨跌幅
    change_pct = Column(Float)
    # 换手率
    turnover_rate = Column(Float)


from zvt.domain.quotes.block import *
from zvt.domain.quotes.stock import *
from zvt.domain.quotes.etf import *
from zvt.domain.quotes.index import *
from zvt.domain.quotes.trade_day import *
