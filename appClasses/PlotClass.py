import plotly.graph_objs as go
import datetime

class PlotClass:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe
    # Function to plot candlestick chart with MAs and buy/sell signals
    def plot_mac_chart(self, df, s_ma, l_ma):
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

        layout = go.Layout(title=f'Moving Averages Cross ({s_ma} and {l_ma}), Timeframe: {self.timeframe} and Buy/Sell Signals for {self.symbol}',
                        xaxis=dict(title='Time'),
                        yaxis=dict(title='Price'))

        # fig = go.Figure(data=[candlestick, short_ma, long_ma], layout=layout)
        fig = go.Figure(data=[candlestick, short_ma, long_ma, buy_signals, sell_signals], layout=layout)
        fig.show()
    

