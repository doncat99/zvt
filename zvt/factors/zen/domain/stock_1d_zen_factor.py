# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base

from zvt.api.data_type import Region, Provider
from zvt.contract.register import register_schema
from zvt.factors.zen.domain.common import ZenFactorCommon

Stock1dZenFactorBase = declarative_base()


class Stock1dZenFactor(Stock1dZenFactorBase, ZenFactorCommon):
    __tablename__ = 'stock_1d_zen_factor'


register_schema(regions=[Region.CHN, Region.US],
                providers={Region.CHN: [Provider.ZVT],
                           Region.US: [Provider.ZVT]},
                db_name='stock_1d_zen_factor',
                schema_base=Stock1dZenFactorBase)


# the __all__ is generated
__all__ = ['Stock1dZenFactor']
