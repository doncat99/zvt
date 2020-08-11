# -*- coding: utf-8 -*-

import pandas as pd

from zvt.factors.factor import Scorer, Transformer
from zvt.utils.pd_utils import normal_index_df


def ma(s, window=5):
    """

    :param s:
    :type s:pd.Series
    :param window:
    :type window:
    :return:
    :rtype:
    """
    return s.rolling(window=window, min_periods=window).mean()


def ema(s, window=12):
    return s.ewm(span=window, adjust=False, min_periods=window).mean()


def macd(s, slow=26, fast=12, n=9, return_type='df', normal=False):
    # 短期均线
    ema_fast = ema(s, window=fast)
    # 长期均线
    ema_slow = ema(s, window=slow)

    # 短期均线 - 长期均线 = 趋势的力度
    diff = ema_fast - ema_slow
    # 力度均线
    dea = diff.ewm(span=n, adjust=False).mean()

    # 力度 的变化
    m = (diff - dea) * 2

    # normal it
    if normal:
        diff = diff / s
        dea = dea / s
        m = m / s

    if return_type == 'se':
        return diff, dea, m
    else:
        return pd.DataFrame({'diff': diff, 'dea': dea, 'macd': m})


class MaTransformer(Transformer):
    def __init__(self, windows=[5, 10], cal_change_pct=False) -> None:
        super().__init__()
        self.windows = windows
        self.cal_change_pct = cal_change_pct

    def transform(self, input_df) -> pd.DataFrame:
        if self.cal_change_pct:
            input_df['change_pct'] = input_df['close'].pct_change()

        for window in self.windows:
            col = 'ma{}'.format(window)
            self.indicators.append(col)

            ma_df = input_df['close'].groupby(level=0).rolling(window=window, min_periods=window).mean()
            ma_df = ma_df.reset_index(level=0, drop=True)
            input_df[col] = ma_df

        return input_df


def point_in_range(point, range):
    return range[0] <= point <= range[1]


def intersect_ranges(range_list):
    result = intersect(range_list[0], range_list[1])
    for range_i in range_list[2:]:
        result = intersect(result, range_i)
    return result


def intersect(range_a, range_b):
    if not range_a or not range_b:
        return None
    # 包含
    if point_in_range(range_a[0], range_b) and point_in_range(range_a[1], range_b):
        return range_a
    if point_in_range(range_b[0], range_a) and point_in_range(range_b[1], range_a):
        return range_b

    if point_in_range(range_a[0], range_b):
        return range_a[0], range_b[1]

    if point_in_range(range_b[0], range_a):
        return range_b[0], range_a[1]
    return None


class IntersectTransformer(Transformer):
    def __init__(self, kdata_overlap=0) -> None:
        super().__init__()
        self.kdata_overlap = kdata_overlap

    def transform(self, input_df) -> pd.DataFrame:
        if self.kdata_overlap > 0:
            # 没有重叠，区间就是(0,0)
            input_df['overlap'] = [(0, 0)] * len(input_df.index)

            def cal_overlap(s):
                high = input_df.loc[s.index, 'high']
                low = input_df.loc[s.index, 'low']
                intersection = intersect_ranges(list(zip(low.to_list(), high.to_list())))
                if intersection:
                    # 设置column overlap为intersection,即重叠区间
                    input_df.at[s.index[-1], 'overlap'] = intersection
                return 0

            input_df[['high', 'low']].groupby(level=0).rolling(window=self.kdata_overlap,
                                                               min_periods=self.kdata_overlap).apply(
                cal_overlap, raw=False)

        return input_df


class MaAndVolumeTransformer(Transformer):
    def __init__(self, windows=[5, 10], vol_windows=[30], kdata_overlap=0) -> None:
        super().__init__()
        self.windows = windows
        self.vol_windows = vol_windows
        self.kdata_overlap = kdata_overlap

    def transform(self, input_df) -> pd.DataFrame:
        for window in self.windows:
            col = 'ma{}'.format(window)
            self.indicators.append(col)

            ma_df = input_df['close'].groupby(level=0).rolling(window=window, min_periods=window).mean()
            ma_df = ma_df.reset_index(level=0, drop=True)
            input_df[col] = ma_df

        for vol_window in self.vol_windows:
            col = 'vol_ma{}'.format(vol_window)
            self.indicators.append(col)

            vol_ma_df = input_df['volume'].groupby(level=0).rolling(window=vol_window, min_periods=vol_window).mean()
            vol_ma_df = vol_ma_df.reset_index(level=0, drop=True)
            input_df[col] = vol_ma_df

        if self.kdata_overlap > 0:
            input_df['overlap'] = [(0, 0)] * len(input_df.index)

            def cal_overlap(s):
                high = input_df.loc[s.index, 'high']
                low = input_df.loc[s.index, 'low']
                intersection = intersect_ranges(list(zip(low.to_list(), high.to_list())))
                if intersection:
                    input_df.at[s.index[-1], 'overlap'] = intersection
                return 0

            input_df[['high', 'low']].groupby(level=0).rolling(window=self.kdata_overlap,
                                                               min_periods=self.kdata_overlap).apply(
                cal_overlap, raw=False)

        return input_df


class MacdTransformer(Transformer):
    def __init__(self, slow=26, fast=12, n=9, normal=False) -> None:
        super().__init__()
        self.slow = slow
        self.fast = fast
        self.n = n
        self.normal = normal

        self.indicators.append('diff')
        self.indicators.append('dea')
        self.indicators.append('macd')

    def transform(self, input_df) -> pd.DataFrame:
        macd_df = input_df.groupby(level=0)['close'].apply(
            lambda x: macd(x, slow=self.slow, fast=self.fast, n=self.n, return_type='df', normal=self.normal))
        input_df = pd.concat([input_df, macd_df], axis=1, sort=False)
        return input_df


class RankScorer(Scorer):
    def __init__(self, ascending=True) -> None:
        self.ascending = ascending

    def score(self, input_df) -> pd.DataFrame:
        result_df = input_df.groupby(level=1).rank(ascending=self.ascending, pct=True)
        return result_df


class QuantileScorer(Scorer):
    def __init__(self, score_levels=[0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]) -> None:
        self.score_levels = score_levels

    def score(self, input_df):
        self.score_levels.sort(reverse=True)

        quantile_df = input_df.groupby(level=1).quantile(self.score_levels)
        quantile_df.index.names = [self.time_field, 'score']

        self.logger.info('factor:{},quantile:\n{}'.format(self.factor_name, quantile_df))

        result_df = input_df.copy()
        result_df.reset_index(inplace=True, level='entity_id')
        result_df['quantile'] = None
        for timestamp in quantile_df.index.levels[0]:
            length = len(result_df.loc[result_df.index == timestamp, 'quantile'])
            result_df.loc[result_df.index == timestamp, 'quantile'] = [quantile_df.loc[
                                                                           timestamp].to_dict()] * length

        self.logger.info('factor:{},df with quantile:\n{}'.format(self.factor_name, result_df))

        # result_df = result_df.set_index(['entity_id'], append=True)
        # result_df = result_df.sort_index(level=[0, 1])
        #
        # self.logger.info(result_df)
        #
        def calculate_score(df, factor_name, quantile):
            original_value = df[factor_name]
            score_map = quantile.get(factor_name)
            min_score = self.score_levels[-1]

            if original_value < score_map.get(min_score):
                return 0

            for score in self.score_levels[:-1]:
                if original_value >= score_map.get(score):
                    return score

        for factor in input_df.columns.to_list():
            result_df[factor] = result_df.apply(lambda x: calculate_score(x, factor, x['quantile']),
                                                axis=1)

        result_df = result_df.reset_index()
        result_df = normal_index_df(result_df)
        result_df = result_df.loc[:, self.factors]

        result_df = result_df.loc[~result_df.index.duplicated(keep='first')]

        self.logger.info('factor:{},df:\n{}'.format(self.factor_name, result_df))

        return result_df
