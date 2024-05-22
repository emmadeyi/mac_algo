import constants.defs as defs
from appClasses.MTClass import MTClass
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import pytz

class SymbolCollectionClass:

    SYMBOL_FILTERS = "*USD*, *EUR*, *GBP*, *JPY*, *NZD*, *CAD*, *AUD*, *CHF*"
    PREFERRED_SYMBOLS = ['USD', 'EUR', 'GBP', 'JPY', 'NZD', 'CAD', 'AUD', 'CHF']

    def __init__(self):
        self.symbols = {}

    # Get symbols
    def get_symbols(self, filter=""):
        try:
            symbols = mt5.symbols_get(filter)
            all_symbols_names = []
            selected_symbols = []
            if symbols:
                for s in symbols:
                    all_symbols_names.append(s.name)
                for symbol_1 in defs.PREFERRED_SYMBOLS:
                    for symbol_2 in defs.PREFERRED_SYMBOLS:
                        s = f"{symbol_1}{symbol_2}"
                        # print(all_symbols_names)        
                        if s in all_symbols_names:
                            selected_symbols.append(s)
            return selected_symbols
        except Exception as error:
            return mt5.last_error()

    # Get symbols with filter
    def get_symbols_with_info(self, filter=""):
        symbols = mt5.symbols_get(filter)
        for s in symbols:        
            symbol_info_dict = mt5.symbol_info(s.name)._asdict()
        return symbol_info_dict
    
    # Get symbols information
    def get_symbol_info(self, symbol):
        symbol = mt5.symbol_info(symbol)._asdict()
        return symbol
    
    def get_symbol_piplocation(self, symbol):
        if symbol:
            symbol = self.get_symbol_info(symbol) 
            return symbol['point'] * 10
    
    def get_ohlc_range(self, pair, timeframe):
        timezone = pytz.timezone("UTC")
        # create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
        utc_from = datetime(2023, 1, 1, tzinfo=timezone)
        utc_to = datetime.now(timezone)
        return mt5.copy_rates_range(pair, timeframe, utc_from, utc_to)

    def data_to_pd(self, data):
        return pd.DataFrame(data)

    def fetch_candles(self, pair_name, granularity = "H1", count=10000): 
        if MTClass.authorize:
            # create DataFrame out of the obtained data
            rates_frame = self.data_to_pd(self.get_ohlc_range(pair_name, defs.TIMEFRAMES[granularity]))
            
            # convert time in seconds into the 'datetime' format
            epoch = pd.to_datetime('1970-01-01')
            
            rates_frame['time'] = epoch + pd.to_timedelta(rates_frame['time'], unit='s')
            # rates_frame['time']= epoch + pd.to_datetime(rates_frame['time'], unit='s')
            # return rates_frame.tail(count)
            return rates_frame
        else:
            return "failed to connect to trade account, error code =",mt5.last_error()
        
    def fetch_candles_counts(self, pair_name, timeframe = mt5.TIMEFRAME_M1, count=10000): 
        if MTClass.authorize:
            # create DataFrame out of the obtained data            
            rates = mt5.copy_rates_from_pos(pair_name, timeframe, 0, count)            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        else:
            return "failed to connect to trade account, error code =",mt5.last_error()
        

    def create_csv_data_file(self, data, pair, timeframe):
        filename = "{}{}_{}.csv".format(defs.HISTORICAL_DATA_FILE_PATH,pair,timeframe)
        file = open(filename, "w")
        if file.write(data.to_csv()):
            print(f"{filename} data file created")
        file.close()
        return

    def get_symbol_data(self, symbol, timeframe):
        return self.fetch_candles(symbol, timeframe)
    
    def get_historical_data(self, symbols, timeframe):
        symbols = self.get_symbols(symbols)
        for symbol in symbols:
            ohlc_data = self.fetch_candles(symbol, timeframe)
            self.create_csv_data_file(ohlc_data, symbol, timeframe)
        return

    def fetch_historical_data(self, symbols, timeframe_list):
        # Fetch Historical Data
        print(f"Fetching Multiple Timeframe Historical Data for {len(symbols)} symbols: {', '.join(symbols)}...")
        print("=================================")
        for symbol in symbols:
            for timeframe in timeframe_list:
                self.get_historical_data(symbol, timeframe)
        print("=================================")
        print("Fetching Historical Data... - Complete")
        print("Historical data Fetched")

    def fetch_historical_data_per_timeframe(self, symbols, timeframe):
        # Fetch Historical Data
        print(f"Fetching Historical Data for {len(symbols)} symbols: {', '.join(symbols)}...")
        print("=================================")
        for symbol in symbols:
            self.get_historical_data(symbol, timeframe)
        print("=================================")
        print("Fetching Historical Data... - Complete")
        print("Historical data Fetched")