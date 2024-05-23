import MetaTrader5 as mt
from appClasses.MTClass import MTClass
from appClasses.SymbolCollectionClass import SymbolCollectionClass
import plotly.graph_objs as go
import datetime

class IndicatorsClass:
    def __init__(self):        
        self.kill_zones = [(7, 10), (12, 15), (19, 22)]  # London, NY Open, and Asian session times in UTC
    # def is_kill_zone(self):
        #     now = datetime.utcnow()
        #     current_hour = now.hour
        #     for start, end in self.kill_zones:
        #         if start <= current_hour < end:
        #             return True
        #     return False

    def is_kill_zone(self, current_hour):
        for start, end in self.kill_zones:
            if start <= current_hour < end:
                return True
        return False

    # Function to calculate moving averages
    def moving_average(self, df, period=10):            
        df['sma'] = df['close'].rolling(window=period).mean()
        return df
    
    def moving_averages_cross(self, df, short_ma=5, long_ma=10, kill_zone=True):
        df['short_ma'] = df['close'].rolling(window=short_ma).mean()
        df['long_ma'] = df['close'].rolling(window=long_ma).mean()        
        # return df
        return self.mac_signals(df, kill_zone)

    # Function to determine buy and sell signals based on MA cross
    def mac_signals(self, df, kill_zone=True):
        # df = self.df
        signals = []
        for i in range(1, len(df)):
            current_hour = df['time'][i].hour
            if self.is_kill_zone(current_hour):
                if df['short_ma'][i] > df['long_ma'][i] and df['short_ma'][i - 1] <= df['long_ma'][i - 1]:
                    signals.append('buy')                
                elif df['short_ma'][i] < df['long_ma'][i] and df['short_ma'][i - 1] >= df['long_ma'][i - 1]:
                    signals.append('sell')
                else:
                    signals.append('')
            else:
                if df['short_ma'][i] > df['long_ma'][i] and df['short_ma'][i - 1] <= df['long_ma'][i - 1]:
                    signals.append('buy Outside KZ') if kill_zone else signals.append('buy')               
                elif df['short_ma'][i] < df['long_ma'][i] and df['short_ma'][i - 1] >= df['long_ma'][i - 1]:
                    signals.append('sell Outside KZ') if kill_zone else signals.append('sell')  
                else:
                    signals.append('')
        signals.append('')  # Append empty string for the last candle
        df['signals'] = signals
        return df

    

