import MetaTrader5 as mt
from appClasses.MTClass import MTClass
from appClasses.SymbolCollectionClass import SymbolCollectionClass
import plotly.graph_objs as go
import datetime

# Connect to MetaTrader 5
mt5 = MTClass()
sc = SymbolCollectionClass()

class MovingAverageCross:
    def __init__(self, symbol, data_timeframe = mt.TIMEFRAME_M1, short_ma = 9, long_ma = 21, candles = 150, lot_size=0.1, risk_reward_ratio=2):
        self.symbol = symbol
        self.lot_size = lot_size
        self.short_ma = short_ma
        self.long_ma = long_ma
        self.candles = candles
        self.data_timeframe = data_timeframe
        self.risk_reward_ratio = risk_reward_ratio
        self.deviation = 20
        self.kill_zones = [(7, 10), (12, 15), (19, 22)]  # London, NY Open, and Asian session times in UTC

    def is_kill_zone(self):
        now = datetime.utcnow()
        current_hour = now.hour
        for start, end in self.kill_zones:
            if start <= current_hour < end:
                return True
        return False

    # Function to calculate moving averages
    def calculate_moving_averages(self, df, short_ma, long_ma):
        df['short_ma'] = df['close'].rolling(window=short_ma).mean()
        df['long_ma'] = df['close'].rolling(window=long_ma).mean()
        return df

    # Function to determine buy and sell signals based on MA cross
    def get_signals(self, df):
        signals = []
        for i in range(1, len(df)):
            if df['short_ma'][i] > df['long_ma'][i] and df['short_ma'][i - 1] <= df['long_ma'][i - 1]:
                signals.append('buy')
                
            elif df['short_ma'][i] < df['long_ma'][i] and df['short_ma'][i - 1] >= df['long_ma'][i - 1]:
                signals.append('sell')
            else:
                signals.append('')
        signals.append('')  # Append empty string for the last candle
        return signals

    # Function to plot candlestick chart with MAs and buy/sell signals
    def plot_chart(self, df):
        candlestick = go.Candlestick(x=df['time'],
                                    open=df['open'],
                                    high=df['high'],
                                    low=df['low'],
                                    close=df['close'],
                                    name='Candlesticks')

        short_ma = go.Scatter(x=df['time'], y=df['short_ma'], mode='lines', name='Short MA', line=dict(color='blue'))
        long_ma = go.Scatter(x=df['time'], y=df['long_ma'], mode='lines', name='Long MA', line=dict(color='red'))

        buy_signals = go.Scatter(x=df['time'][df['signals'] == 'buy'], y=df['close'][df['signals'] == 'buy'],
                                mode='markers', name='Buy Signals', marker=dict(color='green', symbol='triangle-up', size=10))
        sell_signals = go.Scatter(x=df['time'][df['signals'] == 'sell'], y=df['close'][df['signals'] == 'sell'],
                                mode='markers', name='Sell Signals', marker=dict(color='red', symbol='triangle-down', size=10))

        layout = go.Layout(title=f'Moving Averages Cross ({self.short_ma} and {self.long_ma}), Timeframe: {self.data_timeframe} and Buy/Sell Signals for {self.symbol}',
                        xaxis=dict(title='Time'),
                        yaxis=dict(title='Price'))

        # fig = go.Figure(data=[candlestick, short_ma, long_ma], layout=layout)
        fig = go.Figure(data=[candlestick, short_ma, long_ma, buy_signals, sell_signals], layout=layout)
        fig.show()

    def main(self):
        # User-defined parameters
        symbol = self.symbol
        timeframe = self.data_timeframe
        num_candles = self.candles
        short_ma = self.short_ma
        long_ma = self.long_ma

        # Retrieve historical price data
        # df = sc.fetch_candles(symbol, timeframe, num_candles)
        df = sc.fetch_candles_counts(symbol, timeframe, num_candles)

        # # Calculate moving averages
        df = self.calculate_moving_averages(df, short_ma, long_ma)

        return df

if __name__ == '__main__':    
    macross = MovingAverageCross('EURUSD', mt.TIMEFRAME_M1, 7, 12, 200)
    df = macross.main()

    # # Determine buy and sell signals
    df['signals'] = macross.get_signals(df)
    # # Plot the candlestick chart with MAs and buy/sell signals
    macross.plot_chart(df)
    

