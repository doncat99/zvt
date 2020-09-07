import warnings
warnings.filterwarnings("ignore")

import os
import time
from datetime import datetime, timedelta
from functools import wraps
import multiprocessing

from tqdm import tqdm
import pickle

from zvt import zvt_env
from zvt.contract.common import Region
from zvt.domain import Stock, Etf, StockTradeDay, StockSummary, StockDetail, FinanceFactor, \
                       BalanceSheet, IncomeStatement, CashFlowStatement, StockMoneyFlow, \
                       DividendFinancing, DividendDetail, RightsIssueDetail, SpoDetail, \
                       MarginTradingSummary, CrossMarketSummary, HolderTrading, TopTenHolder, \
                       TopTenTradableHolder, StockValuation, EtfStock, EtfValuation, Stock1dKdata, \
                       Stock1dHfqKdata, Stock1dHfqKdata, Stock1wkKdata, Stock1wkHfqKdata, \
                       Stock1monKdata, Stock1monHfqKdata, Stock1monHfqKdata, Stock1monHfqKdata, \
                       Stock1mKdata, Stock1mHfqKdata, Stock1mHfqKdata, Stock5mKdata, Stock5mHfqKdata, \
                       Stock15mKdata, Stock15mHfqKdata, Stock30mKdata, Stock30mHfqKdata, \
                       Stock1hKdata, Stock1hHfqKdata, Etf1dKdata


def get_cache():
    file = zvt_env['cache_path'] + '/' + 'cache.pkl'
    if os.path.exists(file) and os.path.getsize(file) > 0:
        with open(file, 'rb') as handle:
            return pickle.load(handle)
    return {}

def valid(region: Region, func_name, valid_time, data):
    key = "{}_{}".format(region.value, func_name)
    lasttime = data.get(key, None)
    if lasttime is not None:
        if lasttime > (datetime.now() - timedelta(hours=valid_time)):
            return True
    return False

def dump(region: Region, func_name, data):
    key = "{}_{}".format(region.value, func_name)
    file = zvt_env['cache_path'] + '/' + 'cache.pkl'
    with open(file, 'wb+') as handle:
        data.update({key : datetime.now()})
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


class interface():
    @staticmethod
    def get_stock_list_data(provider):
        # 股票列表
        Stock.record_data(provider=provider, sleeping_time=0)

    @staticmethod
    def get_etf_list(provider):
        Etf.record_data(provider=provider, sleeping_time=0)

    @staticmethod
    def get_stock_trade_day(provider, lock, region):
        # 交易日
        StockTradeDay.record_data(provider=provider, share_para=(0, 'Trade Day', lock, True, region), sleeping_time=0)

    @staticmethod
    def get_stock_summary_data(provider, arg1, arg2, arg3, arg4):
        # 市场整体估值
        StockSummary.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_detail_data(provider, arg1, arg2, arg3, arg4):
        # 个股详情
        StockDetail.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_finance_data(provider, arg1, arg2, arg3, arg4):
        # 主要财务指标
        FinanceFactor.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_balance_data(provider, arg1, arg2, arg3, arg4):
        # 资产负债表
        BalanceSheet.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_income_data(provider, arg1, arg2, arg3, arg4):
        # 收益表
        IncomeStatement.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_cashflow_data(provider, arg1, arg2, arg3, arg4):
        # 现金流量表
        CashFlowStatement.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])
    
    @staticmethod
    def get_moneyflow_data(provider, arg1, arg2, arg3, arg4):
        # 股票资金流向表
        StockMoneyFlow.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])
    
    @staticmethod
    def get_dividend_financing_data(provider, arg1, arg2, arg3, arg4):
        # 除权概览表
        DividendFinancing.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_dividend_detail_data(provider, arg1, arg2, arg3, arg4):
        # 除权具细表
        DividendDetail.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_rights_issue_detail_data(provider, arg1, arg2, arg3, arg4):
        # 配股表
        RightsIssueDetail.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_spo_detail_data(provider, arg1, arg2, arg3, arg4):
        # 现金增资
        SpoDetail.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_margin_trading_summary_data(provider, arg1, arg2, arg3, arg4):
        # 融资融券概况
        MarginTradingSummary.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_cross_market_summary_data(provider, arg1, arg2, arg3, arg4):
        # 北向/南向成交概况
        CrossMarketSummary.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_holder_trading_data(provider, arg1, arg2, arg3, arg4):
        # 股东交易
        HolderTrading.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_top_ten_holder_data(provider, arg1, arg2, arg3, arg4):
        # 前十股东表
        TopTenHolder.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_top_ten_tradable_holder_data(provider, arg1, arg2, arg3, arg4):
        # 前十可交易股东表
        TopTenTradableHolder.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_valuation_data(provider, arg1, arg2, arg3, arg4):
        # 个股估值数据
        StockValuation.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_etf_stock_data(provider, arg1, arg2, arg3, arg4):
        # ETF股票
        EtfStock.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_etf_valuation_data(provider, arg1, arg2, arg3, arg4):
        # ETF估值数据
        EtfValuation.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_1d_k_data(provider, arg1, arg2, arg3, arg4):
        # 日线
        Stock1dKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_1d_hfq_k_data(provider, arg1, arg2, arg3, arg4):
        # 日线复权
        Stock1dHfqKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_1w_k_data(provider, arg1, arg2, arg3, arg4):
        # 周线
        Stock1wkKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_1w_hfq_k_data(provider, arg1, arg2, arg3, arg4):
        # 周线复权
        Stock1wkHfqKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])
    
    @staticmethod
    def get_stock_1mon_k_data(provider, arg1, arg2, arg3, arg4):
        # 月线
        Stock1monKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_1mon_hfq_k_data(provider, arg1, arg2, arg3, arg4):
        # 月线复权
        Stock1monHfqKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_1m_k_data(provider, arg1, arg2, arg3, arg4):
        # 1分钟线
        Stock1mKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_1m_hfq_k_data(provider, arg1, arg2, arg3, arg4):
        # 1分钟线复权
        Stock1mHfqKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_5m_k_data(provider, arg1, arg2, arg3, arg4):
        # 5分钟线
        Stock5mKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_5m_hfq_k_data(provider, arg1, arg2, arg3, arg4):
        # 5分钟线复权
        Stock5mHfqKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_15m_k_data(provider, arg1, arg2, arg3, arg4):
        # 15分钟线
        Stock15mKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_15m_hfq_k_data(provider, arg1, arg2, arg3, arg4):
        # 15分钟线复权
        Stock15mHfqKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_30m_k_data(provider, arg1, arg2, arg3, arg4):
        # 30分钟线
        Stock30mKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_30m_hfq_k_data(provider, arg1, arg2, arg3, arg4):
        # 30分钟线复权
        Stock30mHfqKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_1h_k_data(provider, arg1, arg2, arg3, arg4):
        # 1小时线
        Stock1hKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_stock_1h_hfq_k_data(provider, arg1, arg2, arg3, arg4):
        # 1小时线复权
        Stock1hHfqKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])

    @staticmethod
    def get_etf_1d_k_data(provider, arg1, arg2, arg3, arg4):
        Etf1dKdata.record_data(provider=provider, share_para=(arg1, arg2, arg3, False, arg4[2]), sleeping_time=arg4[0], batch_size=arg4[1])


def init(l):
    global lock
    lock = l

def mp_tqdm(func, lock, shared=[], args=[], pc=4, reset=False):
    with multiprocessing.Pool(pc, initializer=init, initargs=(lock,), maxtasksperchild = 1 if reset else None) as p:
        data = get_cache()
        # args = [arg for arg in args if not valid(shared[2], arg[0].__name__, arg[3], data)]
        # The master process tqdm bar is at Position 0
        with tqdm(total=len(args), ncols=80, desc="total", leave=True) as pbar:
            for func_name in p.imap_unordered(func, [[pc, shared, arg] for arg in args], chunksize=1):
                lock.acquire()
                pbar.update()
                if func_name is not None: dump(shared[2], func_name, data)
                lock.release()
                time.sleep(1)

def run(args):
    pc, shared, argset = args
    try:
        argset[0](argset[1], pc, argset[2], lock, shared)
        return argset[0].__name__
    except Exception as e:
        print(e)
    return None


data_set_chn = [
    [interface.get_dividend_financing_data, "eastmoney", "Divdend Financing", 24*6],
    [interface.get_top_ten_holder_data, "eastmoney", "Top Ten Holder", 24*6],
    [interface.get_finance_data, "eastmoney", "Finance Factor", 24*6],
    [interface.get_balance_data, "eastmoney", "Balance Sheet", 24*6],
    [interface.get_top_ten_tradable_holder_data, "eastmoney", "Top Ten Tradable Holder", 24*6],
    [interface.get_income_data, "eastmoney", "Income Statement", 24*6],
    [interface.get_moneyflow_data, "sina", "MoneyFlow Statement", 24],
    [interface.get_dividend_detail_data, "eastmoney", "Divdend Detail", 24],
    [interface.get_spo_detail_data, "eastmoney", "SPO Detail", 24],
    [interface.get_rights_issue_detail_data, "eastmoney", "Rights Issue Detail", 24],
    [interface.get_holder_trading_data, "eastmoney", "Holder Trading", 24],
    [interface.get_etf_valuation_data, "joinquant", "ETF Valuation", 24],
    [interface.get_stock_summary_data, "joinquant", "Stock Summary", 24],  
    [interface.get_stock_detail_data, "eastmoney", "Stock Detail", 24], 
    [interface.get_cashflow_data, "eastmoney", "CashFlow Statement", 24],
    [interface.get_stock_valuation_data, "joinquant", "Stock Valuation", 24],
    [interface.get_etf_stock_data, "joinquant", "ETF Stock", 24],
    [interface.get_margin_trading_summary_data, "joinquant", "Margin Trading Summary", 24],
    [interface.get_cross_market_summary_data, "joinquant", "Cross Market Summary", 24],

    [interface.get_stock_1d_k_data, "joinquant", "Stock Daily K-Data", 24], 
    # [interface.get_stock_1d_hfq_k_data, "joinquant", "Stock Daily HFQ K-Data", 24],
    # [interface.get_stock_1w_k_data, "joinquant", "Stock Weekly K-Data", 24],
    # [interface.get_stock_1w_hfq_k_data, "joinquant", "Stock Weekly HFQ K-Data", 24],
    # [interface.get_stock_1mon_k_data, "joinquant", "Stock Monthly K-Data", 24], 
    # [interface.get_etf_1d_k_data, "sina", "ETF Daily K-Data", 24],

    # [interface.get_stock_1mon_hfq_k_data, "joinquant", "Stock Monthly HFQ K-Data", 24],
    # [interface.get_stock_1h_k_data, "joinquant", "Stock 1 hours K-Data", 24], 
    # [interface.get_stock_1h_hfq_k_data, "joinquant", "Stock 1 hours HFQ K-Data", 24],
    # [interface.get_stock_30m_k_data, "joinquant", "Stock 30 mins K-Data", 24], 
    # [interface.get_stock_30m_hfq_k_data, "joinquant", "Stock 30 mins K-Data", 24],
    # [interface.get_stock_1m_k_data, "joinquant", "Stock 1 mins K-Data", 24], 
    # [interface.get_stock_1m_hfq_k_data, "joinquant", "Stock 1 mins HFQ K-Data", 24],
    # [interface.get_stock_5m_k_data, "joinquant", "Stock 5 mins K-Data", 24], 
    # [interface.get_stock_5m_hfq_k_data, "joinquant", "Stock 5 mins HFQ K-Data", 24],
    # [interface.get_stock_15m_k_data, "joinquant", "Stock 15 mins K-Data", 24], 
    # [interface.get_stock_15m_hfq_k_data, "joinquant", "Stock 15 mins HFQ K-Data", 24],
]

data_set_us = [
    [interface.get_stock_1d_k_data, "yahoo", "Stock Daily K-Data", 24],
    # [interface.get_stock_1d_hfq_k_data, "yahoo", "Stock Daily HFQ K-Data", 24],
    [interface.get_stock_1w_k_data, "yahoo", "Stock Weekly K-Data", 24],
    # [interface.get_stock_1w_hfq_k_data, "yahoo", "Stock Weekly HFQ K-Data", 24],
    [interface.get_stock_1mon_k_data, "yahoo", "Stock Monthly K-Data", 24], 
    # [interface.get_stock_1mon_hfq_k_data, "yahoo", "Stock Monthly HFQ K-Data", 24],
    # [interface.get_stock_1h_k_data, "yahoo", "Stock 1 hours K-Data", 24], 
    # [interface.get_stock_1h_hfq_k_data, "yahoo", "Stock 1 hours HFQ K-Data", 24],
    # [interface.get_stock_30m_k_data, "yahoo", "Stock 30 mins K-Data", 24], 
    # [interface.get_stock_30m_hfq_k_data, "yahoo", "Stock 30 mins K-Data", 24],
    # [interface.get_stock_15m_k_data, "yahoo", "Stock 15 mins K-Data", 24], 
    # [interface.get_stock_15m_hfq_k_data, "yahoo", "Stock 15 mins HFQ K-Data", 24],
    # [interface.get_stock_5m_k_data, "yahoo", "Stock 5 mins K-Data", 24], 
    # [interface.get_stock_5m_hfq_k_data, "yahoo", "Stock 5 mins HFQ K-Data", 24],
    # [interface.get_stock_1m_k_data, "yahoo", "Stock 1 mins K-Data", 24], 
    # [interface.get_stock_1m_hfq_k_data, "yahoo", "Stock 1 mins HFQ K-Data", 24],
]


def fetch_data(lock, region: Region):
    print("*"*60)
    print("*    Start Fetching Stock information...")
    print("*"*60)

    if region == Region.CHN:
        data_set = data_set_chn
        # interface.get_stock_list_data("joinquant")
        # interface.get_etf_list("joinquant")
        interface.get_stock_trade_day("joinquant", lock, region)

    elif region == Region.US:
        data_set = data_set_us
        # interface.get_stock_list_data("yahoo")
        # interface.get_stock_trade_day("yahoo", lock, region)

    else:
        data_set = []


    print("")
    print("parallel processing...")
    print("")

    sleep = 0
    batch_size = 50

    mp_tqdm(run, lock, shared=[sleep, batch_size, region], args=data_set, pc=3, reset=True)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    l = multiprocessing.Lock()

    fetch_data(l, Region.CHN)
    # fetch_data(l, Region.US)

      
    

    

    
