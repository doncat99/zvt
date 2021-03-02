import pandas as pd

from pyfolio import timeseries 
import pyfolio
import matplotlib.pyplot as plt

from zvt.api.data_type import Region, Provider
from zvt.domain import Stock1dKdata, Stock
from zvt.contract.reader import DataReader


def BackTestStats(account_value):
    df = account_value.copy()
    df = get_daily_return(df)
    DRL_strat = backtest_strat(df)
    perf_func = timeseries.perf_stats
    perf_stats_all = perf_func(returns=DRL_strat,
                               factor_returns=DRL_strat,
                               positions=None, transactions=None, turnover_denom="AGB")
    print(perf_stats_all)
    return perf_stats_all


def BaselineStats(region=Region.US,
                  baseline_ticker='^DJI',
                  baseline_start="2019-01-01",
                  baseline_end="2020-09-30"):

    dji, dow_strat = baseline_strat(region=region,
                                    ticker=baseline_ticker,
                                    start=baseline_start,
                                    end=baseline_end)
    perf_func = timeseries.perf_stats
    perf_stats_all = perf_func(returns=dow_strat,
                               factor_returns=dow_strat,
                               positions=None, transactions=None, turnover_denom="AGB")
    print(perf_stats_all)
    return perf_stats_all


def BackTestPlot(account_value,
                 baseline_start="2019-01-01",
                 baseline_end="2020-09-30",
                 region=Region.US,
                 baseline_ticker='^DJI'):

    df = account_value.copy()
    df = get_daily_return(df)

    dji, dow_strat = baseline_strat(region=region,
                                    ticker=baseline_ticker,
                                    start=baseline_start,
                                    end=baseline_end)
    dji.reset_index(drop=True, inplace=True)

    df['timestamp'] = dji['timestamp']
    df = df.dropna()

    DRL_strat = backtest_strat(df)

    with pyfolio.plotting.plotting_context(font_scale=1.1):
        pyfolio.create_full_tear_sheet(returns=DRL_strat,
                                       benchmark_rets=dow_strat,
                                       set_context=False)


def backtest_strat(df):
    strategy_ret = df.copy()
    strategy_ret['timestamp'] = pd.to_datetime(strategy_ret['timestamp'])
    strategy_ret.set_index('timestamp', drop=False, inplace=True)
    strategy_ret.index = strategy_ret.index.tz_localize('UTC')
    del strategy_ret['timestamp']
    ts = pd.Series(strategy_ret['daily_return'].values, index=strategy_ret.index)
    return ts


def baseline_strat(region, ticker, start, end):
    reader = DataReader(region=region,
                        codes=[ticker],
                        start_timestamp=start,
                        end_timestamp=end,
                        data_schema=Stock1dKdata,
                        entity_schema=Stock,
                        columns=['entity_id', 'timestamp', 'open', 'close', 'high', 'low', 'volume'],
                        provider=Provider.Yahoo)
    dji = reader.data_df
    dji['daily_return'] = dji['close'].pct_change(1)
    dow_strat = backtest_strat(dji)
    return dji, dow_strat


def get_daily_return(df):
    df['daily_return'] = df.account_value.pct_change(1)
    sharpe = (252**0.5) * df['daily_return'].mean()
    df['daily_return'].std()

    annual_return = ((df['daily_return'].mean() + 1)**252 - 1) * 100
    print("annual return: ", annual_return)
    print("sharpe ratio: ", sharpe)
    return df
