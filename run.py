import warnings
warnings.filterwarnings("ignore")

import multiprocessing

from tqdm import tqdm

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
        StockTradeDay.record_data(provider='joinquant', process_index=(0, 'Trade Day', lock, True), sleeping_time=0)

    @staticmethod
    def get_stock_summary_data(arg1, arg2, arg3, arg4):
        # 市场整体估值
        StockSummary.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_detail_data(arg1, arg2, arg3, arg4):
        # 个股详情
        StockDetail.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_finance_data(arg1, arg2, arg3, arg4):
        # 主要财务指标
        FinanceFactor.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_balance_data(arg1, arg2, arg3, arg4):
        # 资产负债表
        BalanceSheet.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_income_data(arg1, arg2, arg3, arg4):
        # 收益表
        IncomeStatement.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_cashflow_data(arg1, arg2, arg3, arg4):
        # 现金流量表
        CashFlowStatement.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)
    
    @staticmethod
    def get_moneyflow_data(arg1, arg2, arg3, arg4):
        # 股票资金流向表
        StockMoneyFlow.record_data(provider='sina', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)
    
    @staticmethod
    def get_dividend_financing_data(arg1, arg2, arg3, arg4):
        # 除权概览表
        DividendFinancing.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_dividend_detail_data(arg1, arg2, arg3, arg4):
        # 除权具细表
        DividendDetail.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_rights_issue_detail_data(arg1, arg2, arg3, arg4):
        # 配股表
        RightsIssueDetail.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_spo_detail_data(arg1, arg2, arg3, arg4):
        # 现金增资
        SpoDetail.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_margin_trading_summary_data(arg1, arg2, arg3, arg4):
        # 融资融券概况
        MarginTradingSummary.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_cross_market_summary_data(arg1, arg2, arg3, arg4):
        # 北向/南向成交概况
        CrossMarketSummary.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    # @staticmethod
    # def get_institution_investors_data(arg1, arg2, arg3, arg4):
    #     # 机构投资者
    #     InstitutionalInvestorHolder.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    # @staticmethod
    # def get_big_deal_trading_data(arg1, arg2, arg3, arg4):
    #     BigDealTrading.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_holder_trading_data(arg1, arg2, arg3, arg4):
        # 股东交易
        HolderTrading.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_top_ten_holder_data(arg1, arg2, arg3, arg4):
        # 前十股东表
        TopTenHolder.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_top_ten_tradable_holder_data(arg1, arg2, arg3, arg4):
        # 前十可交易股东表
        TopTenTradableHolder.record_data(provider='eastmoney', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_valuation_data(arg1, arg2, arg3, arg4):
        # 个股估值数据
        StockValuation.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_etf_stock_data(arg1, arg2, arg3, arg4):
        # ETF股票
        EtfStock.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_etf_valuation_data(arg1, arg2, arg3, arg4):
        # ETF估值数据
        EtfValuation.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_1d_k_data(arg1, arg2, arg3, arg4):
        # 日线
        Stock1dKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_1d_hfq_k_data(arg1, arg2, arg3, arg4):
        # 日线复权
        Stock1dHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_1d_ma_data(arg1, arg2, arg3, arg4):
        # 日线MA
        Stock1dMaStateStats.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_1w_k_data(arg1, arg2, arg3, arg4):
        # 周线
        Stock1wkKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_1w_hfq_k_data(arg1, arg2, arg3, arg4):
        # 周线复权
        Stock1wkHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)
    
    @staticmethod
    def get_stock_1w_ma_data(arg1, arg2, arg3, arg4):
        # 周线MA
        Stock1wkMaStateStats.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_1mon_k_data(arg1, arg2, arg3, arg4):
        # 月线
        Stock1monKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_1mon_hfq_k_data(arg1, arg2, arg3, arg4):
        # 月线复权
        Stock1monHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_1m_k_data(arg1, arg2, arg3, arg4):
        # 1分钟线
        Stock1mKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_1m_hfq_k_data(arg1, arg2, arg3, arg4):
        # 1分钟线复权
        Stock1mHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_5m_k_data(arg1, arg2, arg3, arg4):
        # 5分钟线
        Stock5mKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_5m_hfq_k_data(arg1, arg2, arg3, arg4):
        # 5分钟线复权
        Stock5mHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_15m_k_data(arg1, arg2, arg3, arg4):
        # 15分钟线
        Stock15mKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_15m_hfq_k_data(arg1, arg2, arg3, arg4):
        # 15分钟线复权
        Stock15mHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_30m_k_data(arg1, arg2, arg3, arg4):
        # 30分钟线
        Stock30mKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_30m_hfq_k_data(arg1, arg2, arg3, arg4):
        # 30分钟线复权
        Stock30mHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_4h_k_data(arg1, arg2, arg3, arg4):
        # 4小时线
        Stock4hKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_stock_4h_hfq_k_data(arg1, arg2, arg3, arg4):
        # 4小时线复权
        Stock4hHfqKdata.record_data(provider='joinquant', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)

    @staticmethod
    def get_etf_1d_k_data(arg1, arg2, arg3, arg4):
        Etf1dKdata.record_data(provider='sina', process_index=(arg1, arg2, arg3, False), sleeping_time=arg4)


def init(l):
    global lock
    lock = l

def mp_tqdm(func, lock, shared=[], args=[], pc=4, reset=False):
    with multiprocessing.Pool(pc, initializer=init, initargs=(lock,), maxtasksperchild = 1 if reset else None) as p:
        # The master process tqdm bar is at Position 0
        with tqdm(total=len(args), desc="total", leave=True) as pbar:
            for _ in p.imap_unordered(func, [[pc, shared, arg] for arg in args]):
                lock.acquire()
                pbar.update()
                lock.release()

def run(args):
    pc, shared, argset = args
    argset[0](pc, argset[1], lock, shared[0])

if __name__ == '__main__':
    multiprocessing.freeze_support()
    l = multiprocessing.Lock()
    cpus = 8
    sleep = 0

    summary_set = [
        [interface.get_stock_summary_data, "Stock Summary"],
        [interface.get_stock_detail_data, "Stock Detail"], 
        [interface.get_finance_data, "Finance Factor"],
        [interface.get_balance_data, "Balance Sheet"],
        [interface.get_income_data, "Income Statement"],
        [interface.get_cashflow_data, "CashFlow Statement"],
        [interface.get_moneyflow_data, "MoneyFlow Statement"],
        [interface.get_dividend_financing_data, "Divdend Financing"],
        [interface.get_dividend_detail_data, "Divdend Detail"],
        [interface.get_spo_detail_data, "SPO Detail"],
        [interface.get_rights_issue_detail_data, "Rights Issue Detail"],
        [interface.get_margin_trading_summary_data, "Margin Trading Summary"],
        [interface.get_cross_market_summary_data, "Cross Market Summary"],
        [interface.get_holder_trading_data, "Holder Trading"],
        [interface.get_top_ten_holder_data, "Top Ten Holder"],
        [interface.get_top_ten_tradable_holder_data, "Top Ten Tradable Holder"],
        [interface.get_stock_valuation_data, "Stock Valuation"],
        [interface.get_etf_stock_data, "ETF Stock"],
        [interface.get_etf_valuation_data, "ETF Valuation"],
    ]
                 
    detail_set = [
        [interface.get_stock_1d_k_data, "Stock Daily K-Data"], 
        [interface.get_stock_1d_hfq_k_data, "Stock Daily HFQ K-Data"],
        [interface.get_stock_1d_ma_data, "Stock Daily Ma Data"],
        [interface.get_stock_1w_k_data, "Stock Weekly K-Data"],
        [interface.get_stock_1w_hfq_k_data, "Stock Weekly HFQ K-Data"],
        [interface.get_stock_1w_ma_data, "Stock Weekly Ma Data"],
        [interface.get_stock_1mon_k_data, "Stock Monthly K-Data"], 
        [interface.get_stock_1mon_hfq_k_data, "Stock Monthly HFQ K-Data"],
        [interface.get_stock_1m_k_data, "Stock 1 mins K-Data"], 
        [interface.get_stock_1m_hfq_k_data, "Stock 1 mins HFQ K-Data"],
        [interface.get_stock_5m_k_data, "Stock 5 mins K-Data"], 
        [interface.get_stock_5m_hfq_k_data, "Stock 5 mins HFQ K-Data"],
        [interface.get_stock_15m_k_data, "Stock 15 mins K-Data"], 
        [interface.get_stock_15m_hfq_k_data, "Stock 15 mins HFQ K-Data"],
        [interface.get_stock_30m_k_data, "Stock 30 mins K-Data"], 
        [interface.get_stock_30m_hfq_k_data, "Stock Daily 30 mins K-Data"],
        [interface.get_stock_4h_k_data, "Stock 4 hours K-Data"], 
        [interface.get_stock_4h_hfq_k_data, "Stock 4 hours HFQ K-Data"],
        [interface.get_etf_1d_k_data, "ETF Daily K-Data"],
    ]

    print("*"*60)
    print("*    Start Fetching General Stock information...")
    print("*"*60)

    interface.get_stock_list_data("joinquant")
    interface.get_etf_list()
    interface.get_stock_trade_day(l)

    print("")
    print("parallel processing...")
    print("")

    mp_tqdm(run, l, shared=[sleep], args=summary_set, pc=cpus, reset=True)
