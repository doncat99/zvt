# -*- coding: utf-8 -*-
from zvt.api.data_type import Region, Provider, EntityType
from zvt.contract import IntervalLevel
from zvt.factors.target_selector import TargetSelector
from zvt.factors.ma.ma_factor import CrossMaFactor
from zvt.factors import BullFactor
from ..context import init_test_context

init_test_context()


class TechnicalSelector(TargetSelector):
    def init_factors(self, entity_ids, entity_schema, exchanges, codes, the_timestamp, start_timestamp,
                     end_timestamp, level):
        bull_factor = BullFactor(region=self.region, entity_ids=entity_ids, entity_schema=entity_schema, exchanges=exchanges,
                                 codes=codes, the_timestamp=the_timestamp, start_timestamp=start_timestamp,
                                 end_timestamp=end_timestamp, provider=Provider.JoinQuant, level=level, adjust_type='qfq')

        self.filter_factors = [bull_factor]


def test_cross_ma_selector():
    region = Region.CHN
    entity_ids = ['stock_sz_000338']
    entity_type = EntityType.Stock
    start_timestamp = '2018-01-01'
    end_timestamp = '2019-06-30'
    my_selector = TargetSelector(region=region,
                                 entity_ids=entity_ids,
                                 entity_schema=entity_type,
                                 start_timestamp=start_timestamp,
                                 end_timestamp=end_timestamp)
    # add the factors
    my_selector \
        .add_filter_factor(CrossMaFactor(region=region,
                                         entity_ids=entity_ids,
                                         start_timestamp=start_timestamp,
                                         end_timestamp=end_timestamp,
                                         computing_window=10,
                                         windows=[5, 10],
                                         need_persist=False,
                                         level=IntervalLevel.LEVEL_1DAY,
                                         adjust_type='qfq'))
    my_selector.run()
    print(my_selector.open_long_df)
    print(my_selector.open_short_df)
    assert 'stock_sz_000338' in my_selector.get_open_short_targets('2018-01-29')


def test_technical_selector():
    selector = TechnicalSelector(region=Region.CHN,
                                 start_timestamp='2019-01-01',
                                 end_timestamp='2019-06-10',
                                 level=IntervalLevel.LEVEL_1DAY,
                                 provider=Provider.JoinQuant)

    selector.run()

    print(selector.get_result_df())

    targets = selector.get_open_long_targets('2019-06-04')

    assert 'stock_sz_000338' not in targets
    assert 'stock_sz_000338' not in targets
    assert 'stock_sz_002572' not in targets
    assert 'stock_sz_002572' not in targets

    targets = selector.get_open_short_targets('2019-06-04')
    assert 'stock_sz_000338' in targets
    assert 'stock_sz_000338' in targets
    assert 'stock_sz_002572' in targets
    assert 'stock_sz_002572' in targets

    selector.move_on(timeout=0)

    targets = selector.get_open_long_targets('2019-06-19')

    assert 'stock_sz_000338' in targets

    assert 'stock_sz_002572' not in targets
