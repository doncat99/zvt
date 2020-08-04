import warnings
warnings.filterwarnings("ignore")

from multiprocessing import freeze_support, Pool, Lock
import time

from zvt.domain import (Stock, StockTradeDay, StockDetail, FinanceFactor, BalanceSheet, \
                        IncomeStatement, CashFlowStatement, DividendFinancing, HolderTrading, \
                        TopTenHolder, TopTenTradableHolder, Stock1dKdata, Stock1dHfqKdata, \
                        Stock1wkKdata, Stock1wkHfqKdata, StockValuation, Etf, EtfStock
                       )


class interface():

    @staticmethod
    def get_stock_list_data(provider):
        Stock.record_data(provider=provider, sleeping_time=0)

    @staticmethod
    def get_stock_trade_day(lock):
        StockTradeDay.record_data(provider='joinquant', process_index=(0, 'Trade Day', lock), sleeping_time=0)

    @staticmethod
    def get_detail_data(arg1, arg2, arg3):
        #this one will take longer, so we'll kill it after the other finishes
        # select * from stock_detail where profile is not null
        StockDetail.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_finance_data(arg1, arg2, arg3):
        # select * from finance_factor
        FinanceFactor.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_balance_data(arg1, arg2, arg3):
        # select * from finance_factor
        BalanceSheet.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_income_data(arg1, arg2, arg3):
        # select * from finance_factor
        IncomeStatement.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_cashflow_data(arg1, arg2, arg3):
        # select * from finance_factor
        CashFlowStatement.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_dividend_financing_data(arg1, arg2, arg3):
        # select * from finance_factor
        DividendFinancing.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_holder_trading_data(arg1, arg2, arg3):
        # select * from finance_factor
        HolderTrading.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_top_ten_holder_data(arg1, arg2, arg3):
        # select * from finance_factor
        TopTenHolder.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_top_ten_tradable_holder_data(arg1, arg2, arg3):
        # select * from finance_factor
        TopTenTradableHolder.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_1d_k_data(arg1, arg2, arg3):
        # select * from finance_factor
        Stock1dKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_1d_hfq_k_data(arg1, arg2, arg3):
        # select * from finance_factor
        Stock1dHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_1w_k_data(arg1, arg2, arg3):
        # select * from finance_factor
        Stock1wkKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_1w_hfq_k_data(arg1, arg2, arg3):
        # select * from finance_factor
        Stock1wkHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_stock_valuation_data(arg1, arg2, arg3):
        # 个股估值数据
        # select * from finance_factor
        StockValuation.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_etf_data(arg1, arg2, arg3):
        # select * from finance_factor
        Etf.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_etf_stock_data(arg1, arg2, arg3):
        # select * from finance_factor
        EtfStock.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)


def run(param):
    param[1](param[0], param[2], lock)

def init(l):
    global lock
    lock = l


if __name__ == '__main__':
    freeze_support()
    l = Lock()

    print("*"*60)
    print("*    Start Fetching General Stock information...")
    print("*"*60)

    interface.get_stock_list_data("eastmoney")

    param_set = [
                 [0, interface.get_detail_data, "Stock Detail"], 
                 [1, interface.get_finance_data, "Finance Factor"],
                 [2, interface.get_balance_data, "Balance Sheet"],
                 [3, interface.get_income_data, "Income Statement"],
                 [4, interface.get_cashflow_data, "CashFlow Statement"],
                 [5, interface.get_dividend_financing_data, "Divdend Financing"],
                 [6, interface.get_holder_trading_data, "Holder Trading"],
                 [7, interface.get_top_ten_holder_data, "Top Ten Holder"],
                 [8, interface.get_top_ten_tradable_holder_data, "Top Ten Tradable Holder"],
                ]

    pool = Pool(len(param_set), initializer=init, initargs=(l,))
    pool.map(run, param_set)
    pool.close()
    pool.join()

    print("*"*60)
    print("*    Start Fetching Stock K-Data set.")
    print("*"*60)

    interface.get_stock_list_data("joinquant")
    interface.get_stock_trade_day(l)

    param_set = [
                 [0, interface.get_1d_k_data, "Daily K-Data"], 
                 [1, interface.get_1d_hfq_k_data, "Daily HFQ K-Data"],
                 [2, interface.get_1w_k_data, "Weekly K-Data"],
                 [3, interface.get_1w_hfq_k_data, "Weekly HFQ K-Data"],
                 [4, interface.get_stock_valuation_data, "Stock Valuation"],
                 [5, interface.get_etf_data, "ETF"],
                 [6, interface.get_etf_stock_data, "ETF Stock"],
                ]

    pool = Pool(3, initializer=init, initargs=(l,))
    pool.map(run, param_set)
    pool.close()
    pool.join()

    print("*"*60)
    print("*    Done Fetching Processes.")
    print("*"*60)