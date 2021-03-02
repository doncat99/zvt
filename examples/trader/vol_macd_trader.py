# -*- coding: utf-8 -*-

from examples.factors.vol_factor import VolFactor
from zvt.api.data_type import Region, Provider
from zvt.contract import IntervalLevel
from zvt.factors import TargetSelector, BullFactor
from zvt.trader.trader import StockTrader


class VolMacdTrader(StockTrader):

    def init_selectors(self, entity_ids, entity_schema, exchanges, codes, start_timestamp, end_timestamp,
                       adjust_type=None):
        # 周线策略
        week_bull_selector = TargetSelector(region=self.region, entity_ids=entity_ids, entity_schema=entity_schema, exchanges=exchanges,
                                            codes=codes, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                                            provider=Provider.JoinQuant, level=IntervalLevel.LEVEL_1WEEK)
        week_bull_factor = BullFactor(entity_ids=entity_ids, entity_schema=entity_schema, exchanges=exchanges,
                                      codes=codes, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                                      provider=Provider.JoinQuant, level=IntervalLevel.LEVEL_1WEEK)
        week_bull_selector.add_filter_factor(week_bull_factor)

        # 日线策略
        day_bull_selector = TargetSelector(region=self.region, entity_ids=entity_ids, entity_schema=entity_schema, exchanges=exchanges,
                                           codes=codes, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                                           provider=Provider.JoinQuant, level=IntervalLevel.LEVEL_1DAY, long_threshold=0.7)
        day_bull_factor = BullFactor(region=self.region, entity_ids=entity_ids, entity_schema=entity_schema, exchanges=exchanges,
                                     codes=codes, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                                     provider=Provider.JoinQuant, level=IntervalLevel.LEVEL_1DAY)
        day_vol_factor = VolFactor(region=self.region, entity_ids=entity_ids, entity_schema=entity_schema, exchanges=exchanges,
                                   codes=codes, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                                   provider=Provider.JoinQuant, level=IntervalLevel.LEVEL_1DAY)
        day_bull_selector.add_filter_factor(day_bull_factor)
        day_bull_selector.add_score_factor(day_vol_factor)

        self.selectors.append(week_bull_selector)
        self.selectors.append(day_bull_selector)


if __name__ == '__main__':
    trader = VolMacdTrader(region=Region.CHN, start_timestamp='2017-01-01', end_timestamp='2017-06-01')
    trader.run()
    # f = VolFactor(start_timestamp='2020-01-01', end_timestamp='2020-04-01')
    # print(f.result_df)
