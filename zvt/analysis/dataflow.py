import logging

import pandas as pd

logger = logging.getLogger(__name__)


class LoadData():
    __db = DataStore()

    def __init__(self, fetcher):
        self.__db.setRegion(self.getRegion())
        self.__fetcher = fetcher
        self.__dailyDataset = {}
        self.__tickDataset = {}

    def getLatestTradeDate(self):
        return self.__fetcher.getLatestTradeDate()

    def getTradeDates(self):
        return self.__fetcher.getTradeDates()

    def updateData(self, symbols=[]):
        return self.__fetcher.updateData(symbols)

    def csvToSql(self):
        self.__fetcher.csvToSql()

    def __loadBasics__(self, basic_cols, basic_def):
        try:
            return self.__db.load(DBApi.BASIC_SHEET,
                                  item='STOCK_LIST',
                                  target=basic_cols,
                                  index='symbol')
        except Exception as e:
            msg = "__loadBasics__ Exception: {}".format(e)
            self.logger.warning(msg)
        return pd.DataFrame()

    @classmethod
    def __loadDailyset__(self, symbol, daily_cols, daily_def):
        try:
            df_daily = self.__db.load(DBApi.DAILY_SHEET,
                                      item=symbol,
                                      target=daily_cols,
                                      daily_def=daily_def)
        except Exception as e:
            msg = "__loadDailyset__ Exception: {}, {}".format(symbol, e)
            self.logger.warning(msg)
            return pd.DataFrame()

        if not df_daily.empty:
            df_daily.dropna(inplace=True)
            df_daily.sort_values(['date'], ascending=True, inplace=True)
            df_daily.reset_index(drop=True, inplace=True)
            return df_daily

        return pd.DataFrame()

    @classmethod
    # @nb.jit(cache=True)
    def __loadTickset__(self, symbol, tick_cols, tick_def, dates):
        try:
            df = self.__db.load(DBApi.TICK_SHEET,
                                symbol=symbol,
                                between=dates,
                                target=tick_cols,
                                tick_def=tick_def,
                                keep_default_na=False)
            return df
        except Exception as e:
            msg = "__loadTickset__ Exception: {}, {}".format(symbol, e)
            self.logger.warning(msg)
        return pd.DataFrame()

    @classmethod
    def __loadDataset__(self, item):
        timeRange, symbol, daily_def, daily_cols, tick_def, tick_cols = item

        df_daily = self.__loadDailyset__(symbol, daily_cols, daily_def)
        if df_daily.empty:
            return None

        if timeRange == DataFlow.RangeTick:
            dates = df_daily['date'].values.tolist()
            df_tick = self.__loadTickset__(symbol, tick_cols, tick_def, dates)
            return (symbol, [df_daily, df_tick])
        else:
            return (symbol, [df_daily])

    def __mergeDataset__(self, ret):
        res = ret[1]
        if res is not None:
            self.__dailyDataset[res[0]] = res[1][0]
            if len(res[1]) > 1:
                self.__tickDataset[res[0]] = res[1][1]

    def __loadEconomicData__(self):
        try:
            df_oil = self.__db.load(DBApi.ECON_SHEET, item='OIL')
            df_oil.rename(columns={'Value': 'oil'}, inplace=True)
            df_usd = self.__db.load(DBApi.ECON_SHEET, item='USD')
            df_usd.rename(columns={'Value': 'usd'}, inplace=True)
            df = pd.merge(df_oil, df_usd, on='date', how='outer', sort=True).fillna(method='ffill')
            return df
        except Exception as e:
            msg = "__loadEconomicData__ Exception: {}".format(e)
            self.logger.warning(msg)
        return pd.DataFrame()

    # @nb.jit(forceobj=True, cache=True)
    def loadData(self, timeRange, updateData=False, symbols=[]):
        if updateData:
            self.updateData(symbols)

        basicDef = Declaration.genDefinition(self.getDataDeclaration(), 'basic')
        basicCols = list(basicDef.keys())

        basic = self.__loadBasics__(basicCols, basicDef)
        if basic.empty:
            msg = "loadData Exception: get basic info failed"
            self.logger.error(msg)
            raise
            # return [pd.DataFrame(), [], []]
        basic.sort_index(ascending=True, inplace=True)

        cache_file = Environment.outpath() + self.getRegion() + "cache_" + \
            str(timeRange) + '_' + self.getLatestTradeDate() + ".pkl"

        economic = self.__loadEconomicData__()

        cacheMode = False
        if len(symbols) == 0:
            cacheMode = True
            dataset = UtilSet.readCache(cache_file)
            if dataset is not None:
                return basic, dataset, economic
            symbols = basic.index.values.tolist()

        dailyDef = Declaration.genDefinition(self.getDataDeclaration(), 'daily')
        dailyCols = list(dailyDef.keys())
        tickDef = Declaration.genDefinition(self.getDataDeclaration(), 'tick')
        tickCols = list(tickDef.keys())

        items = [(timeRange, symbol, dailyDef,
                  dailyCols, tickDef, tickCols) for symbol in symbols]

        imap_unordered_tqdm(func=self.__loadDataset__,
                            callback=self.__mergeDataset__,
                            lock=Environment.getlock(),
                            args=items,
                            pc=Environment.cpus(),
                            desc="Load Data")
        dataset = []
        if len(self.__dailyDataset) > 0:
            dataset.append(self.__dailyDataset)
        if len(self.__tickDataset) > 0:
            dataset.append(self.__tickDataset)
        if cacheMode:
            UtilSet.saveCache(cache_file, dataset)

        return basic, dataset, economic


class DataFlow(LoadData):
    RangeDaily = 0
    RangeTick = 1
    sheet = ['daily', 'tick']

    def __init__(self, fetcher):
        super().__init__(fetcher)
        self.__wrapper = DataWrapper(self.sheet)

    def getWrapper(self):
        return self.__wrapper

    def processDataset(self, dataset, economic):
        ret = []
        for index, data in enumerate(dataset):
            items = [(index, key, value, economic) for key, value in data.items()]
            ret.append(self.getProcesses().imapDict(
                self.customDataProcess, items,
                desc="process {} data".format(self.sheet[index])))
        return ret

    def featureEncode(self, df, index, ft_enc):
        variable_types = Declaration.genFeatureVariable(self.getDataDeclaration(),
                                                        self.sheet[index])
        basic_types = Declaration.genFeatureVariable(self.getDataDeclaration(),
                                                     'basic')
        variable_types.update(basic_types)

        keys = df.columns
        variables = variable_types.keys()
        for key in keys:
            if key not in variables:
                variable_types[key] = ft.variable_types.Numeric

        es = ft.EntitySet(id="stock")
        es.entity_from_dataframe(entity_id="stock_data",
                                 dataframe=df,
                                 make_index=True,
                                 index="index",
                                 variable_types=variable_types)
        # print("stock_data:\n", es["stock_data"].variables)

        if ft_enc is not None:
            return ft.calculate_feature_matrix(ft_enc, es)

        feature_matrix, feature_defs = ft.dfs(entityset=es,
                                              target_entity="stock_data",
                                              agg_primitives=[],
                                              n_jobs=1,
                                              # dask_kwargs={'diagnostics_port':8787},
                                              verbose=True)

        ft_mat_enc, ft_enc = encode_features(feature_matrix,
                                             feature_defs,
                                             inplace=True,
                                             include_unknown=False)
        return ft_mat_enc, ft_enc

    def featureEngineering(self, basic, df, timeRange, ft_enc=None):
        if df.empty:
            return df

        sort_value = [['symbol', 'date'], ['symbol', 'date', 'timestamp']]
        data = df.join(basic, on='symbol')
        data.sort_values(sort_value[timeRange], inplace=True)
        data.reset_index(drop=True, inplace=True)
        return self.featureEncode(data, timeRange, ft_enc)


class DataUS(DataFlow):
    __dataDeclare = Declaration.readDeclaration("DataUS.csv")
    priceColumns = ['close', 'market_close']

    def __init__(self, startDate, customDataProcess=None):
        super().__init__(FetcherStockUS(self.getRegion(), startDate))
        self.customDataProcess = customDataProcess

    @staticmethod
    def getRegion():
        return 'US/'

    @staticmethod
    def getDataDeclaration():
        return DataUS.__dataDeclare


class DataCHN(DataFlow):
    __dataDeclare = Declaration.readDeclaration("DataCHN.csv")
    priceColumns = ['close', 'price']

    def __init__(self, startDate, customDataProcess=None):
        super().__init__(FetcherStockCHN(self.getRegion(), startDate))
        self.customDataProcess = customDataProcess

    @staticmethod
    def getRegion():
        return 'CHN/'

    @staticmethod
    def getDataDeclaration():
        return DataCHN.__dataDeclare
