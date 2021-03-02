# -*- coding: utf-8 -*-
from zvt.api.data_type import Region, Provider
from zvt.api.quote import get_kdata
from zvt.factors.algorithm import MaTransformer, MacdTransformer


def test_ma_transformer():
    df = get_kdata(region=Region.CHN, entity_id='stock_sz_000338',
                   start_timestamp='2019-01-01', provider=Provider.JoinQuant,
                   index=['entity_id', 'timestamp'])

    t = MaTransformer(windows=[5, 10])

    result_df = t.transform(df)

    print(result_df)


def test_MacdTransformer():
    df = get_kdata(region=Region.CHN, entity_id='stock_sz_000338',
                   start_timestamp='2019-01-01',
                   provider=Provider.JoinQuant,
                   index=['entity_id', 'timestamp'])

    t = MacdTransformer()

    result_df = t.transform(df)

    print(result_df)
