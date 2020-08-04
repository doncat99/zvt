# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
# from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from zvt import zvt_env


# all registered providers
providers = []

# all registered entity types
entity_types = []

# all registered schemas
schemas = []

# entity_type -> schema
entity_schema_map = {}

# global sessions
sessions = {}


if "db_engine" in zvt_env and zvt_env['db_engine'] == "postgresql":
    link = 'postgresql+psycopg2://{}:{}@{}/{}'.format(
        zvt_env['db_user'], zvt_env['db_pass'], zvt_env['db_host'], zvt_env['db_name'])
    db_engine = create_engine(link,
                              encoding='utf-8',
                              echo=False,
                              poolclass=QueuePool,
                              pool_size=zvt_env['cpus'],
                              pool_timeout=30,
                              pool_pre_ping=True,
                              max_overflow=10)
    # Base = declarative_base()
    # Base.metadata.create_all(bind=db_engine)
    # url = 'postgresql+psycopg2://{}@{}/{}'.format(zvt_env['db_name'], zvt_env['db_host'], zvt_env['db_user'])
    # if not database_exists(url):
    #     create_database(url)

    # provider_dbname -> engine
    db_engine_map = {
        "joinquant_stock_meta": db_engine,
        
        "eastmoney_block_1d_kdata": db_engine,
        "joinquant_stock_1mon_kdata": db_engine,
        "eastmoney_block_1mon_kdata": db_engine,
        "joinquant_stock_1wk_hfq_kdata": db_engine,
        "eastmoney_block_1wk_kdata": db_engine,
        "joinquant_stock_1wk_kdata": db_engine,
        "eastmoney_dividend_financing": db_engine,
        "joinquant_stock_30m_hfq_kdata": db_engine,
        "eastmoney_finance": db_engine,
        "joinquant_stock_30m_kdata": db_engine,
        "eastmoney_holder": db_engine,
        "joinquant_stock_4h_hfq_kdata": db_engine,
        "eastmoney_stock_meta": db_engine,
        "joinquant_stock_4h_kdata": db_engine,
        "eastmoney_trading": db_engine,
        "joinquant_stock_5m_hfq_kdata": db_engine,
        "exchange_overall": db_engine,
        "joinquant_stock_5m_kdata": db_engine,
        "exchange_stock_meta": db_engine,
        "joinquant_trade_day": db_engine,
        "joinquant_overall": db_engine,
        "joinquant_valuation": db_engine,
        "joinquant_stock_15m_hfq_kdata": db_engine,
        "sina_etf_1d_kdata": db_engine,
        "joinquant_stock_15m_kdata": db_engine,
        "sina_index_1d_kdata": db_engine,
        "joinquant_stock_1d_hfq_kdata": db_engine,
        "sina_money_flow": db_engine,
        "joinquant_stock_1d_kdata": db_engine,
        "sina_stock_meta": db_engine,
        "joinquant_stock_1h_hfq_kdata": db_engine,
        "zvt_stock_1d_ma_factor": db_engine,
        "joinquant_stock_1h_kdata": db_engine,
        "zvt_stock_1d_ma_stats": db_engine,
        "joinquant_stock_1m_hfq_kdata": db_engine,
        "zvt_stock_1d_zen_factor": db_engine,
        "joinquant_stock_1m_kdata": db_engine,
        "zvt_stock_1wk_ma_stats": db_engine,
        "joinquant_stock_1mon_hfq_kdata": db_engine,
        "zvt_trader_info": db_engine,
    }
else:
    db_engine_map = {}


# provider_dbname -> session
db_session_map = {}

# provider -> [db_name1,db_name2...]
provider_map_dbnames = {}

# db_name -> [declarative_base1,declarative_base2...]
dbname_map_base = {}

# db_name -> [declarative_meta1,declarative_meta2...]
dbname_map_schemas = {}

# entity_type -> schema
entity_map_schemas = {}
