import warnings
warnings.filterwarnings("ignore")

from multiprocessing import freeze_support, Pool, Lock
import time

from zvt.domain import *


class interface():

    @staticmethod
    def get_stock_list_data(provider):
        # 股票列表
        Stock.record_data(provider=provider, sleeping_time=0)

    @staticmethod
    def get_etf_list():
        Etf.record_data(provider='joinquant', sleeping_time=0)

    @staticmethod
    def get_stock_trade_day(lock):
        # 交易日
        StockTradeDay.record_data(provider='joinquant', process_index=(0, 'Trade Day', lock), sleeping_time=0)

    @staticmethod
    def get_stock_summary_data(arg1, arg2, arg3):
        # 市场整体估值
        StockSummary.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_stock_detail_data(arg1, arg2, arg3):
        # 个股详情
        StockDetail.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_finance_data(arg1, arg2, arg3):
        # 主要财务指标
        FinanceFactor.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_balance_data(arg1, arg2, arg3):
        # 资产负债表
        BalanceSheet.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_income_data(arg1, arg2, arg3):
        # 收益表
        IncomeStatement.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_cashflow_data(arg1, arg2, arg3):
        # 现金流量表
        CashFlowStatement.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)
    
    @staticmethod
    def get_moneyflow_data(arg1, arg2, arg3):
        # 股票资金流向表
        StockMoneyFlow.record_data(provider='sina', process_index=(arg1, arg2, arg3), sleeping_time=0)
    
    @staticmethod
    def get_dividend_financing_data(arg1, arg2, arg3):
        # 除权概览表
        DividendFinancing.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_dividend_detail_data(arg1, arg2, arg3):
        # 除权具细表
        DividendDetail.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_rights_issue_detail_data(arg1, arg2, arg3):
        # 配股表
        RightsIssueDetail.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_spo_detail_data(arg1, arg2, arg3):
        # 现金增资
        SpoDetail.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_margin_trading_summary_data(arg1, arg2, arg3):
        # 融资融券概况
        MarginTradingSummary.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_cross_market_summary_data(arg1, arg2, arg3):
        # 北向/南向成交概况
        CrossMarketSummary.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    # @staticmethod
    # def get_institution_investors_data(arg1, arg2, arg3):
    #     # 机构投资者
    #     InstitutionalInvestorHolder.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    # @staticmethod
    # def get_big_deal_trading_data(arg1, arg2, arg3):
    #     BigDealTrading.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_holder_trading_data(arg1, arg2, arg3):
        # 股东交易
        HolderTrading.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_top_ten_holder_data(arg1, arg2, arg3):
        # 前十股东表
        TopTenHolder.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_top_ten_tradable_holder_data(arg1, arg2, arg3):
        # 前十可交易股东表
        TopTenTradableHolder.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_stock_valuation_data(arg1, arg2, arg3):
        # 个股估值数据
        StockValuation.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_etf_stock_data(arg1, arg2, arg3):
        EtfStock.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_etf_valuation_data(arg1, arg2, arg3):
        EtfValuation.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_stock_1d_k_data(arg1, arg2, arg3):
        Stock1dKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_stock_1d_hfq_k_data(arg1, arg2, arg3):
        Stock1dHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_stock_1w_k_data(arg1, arg2, arg3):
        Stock1wkKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_stock_1w_hfq_k_data(arg1, arg2, arg3):
        Stock1wkHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3), sleeping_time=0)

    @staticmethod
    def get_etf_1d_k_data(arg1, arg2, arg3):
        Etf1dKdata.record_data(provider='sina', process_index=(arg1, arg2, arg3), sleeping_time=0)


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

    # interface.get_stock_list_data("joinquant")
    # interface.get_etf_list()
    # interface.get_stock_trade_day(l)

    summary_set = [
        [0, interface.get_stock_summary_data, "Stock Summary"],
        [1, interface.get_stock_detail_data, "Stock Detail"], 
        [2, interface.get_finance_data, "Finance Factor"],
        [3, interface.get_balance_data, "Balance Sheet"],
        [4, interface.get_income_data, "Income Statement"],
        [5, interface.get_cashflow_data, "CashFlow Statement"],
        [6, interface.get_moneyflow_data, "MoneyFlow Statement"],
        [7, interface.get_dividend_financing_data, "Divdend Financing"],
        [8, interface.get_dividend_detail_data, "Divdend Detail"],
        [9, interface.get_spo_detail_data, "SPO Detail"],
        [10, interface.get_rights_issue_detail_data, "Rights Issue Detail"],
        [11, interface.get_margin_trading_summary_data, "Margin Trading Summary"],
        [12, interface.get_cross_market_summary_data, "Cross Market Summary"],
        [13, interface.get_holder_trading_data, "Holder Trading"],
        [14, interface.get_top_ten_holder_data, "Top Ten Holder"],
        [15, interface.get_top_ten_tradable_holder_data, "Top Ten Tradable Holder"],
        [16, interface.get_stock_valuation_data, "Stock Valuation"],
        [17, interface.get_etf_stock_data, "ETF Stock"],
        [18, interface.get_etf_valuation_data, "ETF Valuation"],
    ]
                 
    detail_set = [
        [0, interface.get_stock_1d_k_data, "Stock Daily K-Data"], 
        [1, interface.get_stock_1d_hfq_k_data, "Stock Daily HFQ K-Data"],
        [2, interface.get_stock_1w_k_data, "Stock Weekly K-Data"],
        [3, interface.get_stock_1w_hfq_k_data, "Stock Weekly HFQ K-Data"],
        [4, interface.get_etf_1d_k_data, "ETF Daily K-Data"],
    ]
                
    pool = Pool(3, initializer=init, initargs=(l,))
    pool.imap_unordered(run, summary_set)
    pool.close()
    pool.join()

    pool = Pool(3, initializer=init, initargs=(l,))
    pool.imap_unordered(run, detail_set)
    pool.close()
    pool.join()
