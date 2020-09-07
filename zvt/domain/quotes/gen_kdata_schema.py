# -*- coding: utf-8 -*-
import os
from typing import List

from zvt.api import AdjustType
from zvt.contract import IntervalLevel
from zvt.contract.common import Region


# kdata schema rule
# 1)name:{entity_type}{level}Kdata
# 2)one db file for one schema

def gen_kdata_schema(pkg: str, regions: List[Region], providers: List[str], entity_type: str, levels: List[IntervalLevel],
                     adjust_types: List[AdjustType] = [None]):
    tables = []
    for level in levels:
        for adjust_type in adjust_types:
            level = IntervalLevel(level)

            cap_entity_type = entity_type.capitalize()
            cap_level = level.value.capitalize()

            if level != IntervalLevel.LEVEL_TICK:
                kdata_common = f'{cap_entity_type}KdataCommon'
            else:
                kdata_common = f'{cap_entity_type}TickCommon'

            if adjust_type and (adjust_type != AdjustType.qfq):
                class_name = f'{cap_entity_type}{cap_level}{adjust_type.value.capitalize()}Kdata'
                table_name = f'{entity_type}_{level.value}_{adjust_type.value.lower()}_kdata'

            else:
                class_name = f'{cap_entity_type}{cap_level}Kdata'
                table_name = f'{entity_type}_{level.value}_kdata'

            tables.append(table_name)

            schema_template = f'''# -*- coding: utf-8 -*-
# this file is generated by gen_kdata_schema function, dont't change it
from sqlalchemy.ext.declarative import declarative_base

from zvt.contract.register import register_schema
from {pkg}.domain.quotes import {kdata_common}

KdataBase = declarative_base()


class {class_name}(KdataBase, {kdata_common}):
    __tablename__ = '{table_name}'


register_schema(regions={regions}, providers={providers}, db_name='{table_name}', schema_base=KdataBase)

__all__ = ['{class_name}']
'''
            # generate the schema
            with open(os.path.join(entity_type, f'{table_name}.py'), 'w') as outfile:
                outfile.write(schema_template)

        # generate the package
        imports = [f'from {pkg}.domain.quotes.{entity_type}.{table} import *' for table in tables]
        imports_str = '\n'.join(imports)

        package_template = '''# -*- coding: utf-8 -*-
# this file is generated by gen_kdata_schema function, dont't change it
''' + imports_str

        with open(os.path.join(entity_type, '__init__.py'), 'w') as outfile:
            outfile.write(package_template)


if __name__ == '__main__':
    # 股票行情
    gen_kdata_schema(pkg='zvt', regions=[Region.CHN, Region.US], providers=['joinquant'], entity_type='stock',
                     levels=[level for level in IntervalLevel if level != IntervalLevel.LEVEL_TICK],
                     adjust_types=[None, AdjustType.hfq])

    # 板块行情
    gen_kdata_schema(pkg='zvt', regions=[Region.CHN, Region.US], providers=['eastmoney'], entity_type='block',
                     levels=[IntervalLevel.LEVEL_1DAY, IntervalLevel.LEVEL_1WEEK, IntervalLevel.LEVEL_1MON])

    # etf行情
    gen_kdata_schema(pkg='zvt', regions=[Region.CHN, Region.US], providers=['sina'], entity_type='etf',
                     levels=[IntervalLevel.LEVEL_1DAY])
    # 指数行情
    gen_kdata_schema(pkg='zvt', regions=[Region.CHN, Region.US], providers=['sina'], entity_type='index',
                     levels=[IntervalLevel.LEVEL_1DAY])
