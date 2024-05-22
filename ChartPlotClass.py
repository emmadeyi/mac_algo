import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

class ChartPlotClass:
    def __init__(self):
        self.fig, self.ax = plt.subplots()

    def plot_candlestick(self, df):
        df['date_num'] = mdates.date2num(df['time'])
        ohlc = df[['date_num', 'open', 'high', 'low', 'close']].values
        candlestick_ohlc(self.ax, ohlc, width=0.0005, colorup='g', colordown='r', alpha=0.8)

    def plot_indicators(self, df):
        # Plot Moving Averages
        self.ax.plot(df['time'], df['ma_short'], label='MA Short', color='blue', linewidth=0.7)
        self.ax.plot(df['time'], df['ma_long'], label='MA Long', color='red', linewidth=0.7)

        # Plot RSI
        ax2 = self.ax.twinx()
        ax2.plot(df['time'], df['rsi'], label='RSI', color='purple', linewidth=0.7)
        ax2.axhline(70, color='red', linestyle='--', linewidth=0.5)
        ax2.axhline(30, color='green', linestyle='--', linewidth=0.5)
        ax2.set_ylabel('RSI')

        # Plot Supertrend
        self.ax.plot(df['time'], df['supertrend'], label='SuperTrend', color='orange', linewidth=0.7)

        # Plot MACD
        self.ax.plot(df['time'], df['macd'], label='MACD', color='magenta', linewidth=0.7)
        self.ax.plot(df['time'], df['macd_signal'], label='MACD Signal', color='cyan', linewidth=0.7)

        # Plot Order Blocks, Fibonacci levels
        self.ax.plot(df['time'], df['order_block'], label='Order Block', color='black', linestyle='--', linewidth=0.7)
        self.ax.plot(df['time'], df['fib_50'], label='Fibonacci 50%', color='brown', linestyle='--', linewidth=0.7)
        self.ax.plot(df['time'], df['fib_62'], label='Fibonacci 62%', color='grey', linestyle='--', linewidth=0.7)

        # Plot Premium and Discount Ranges
        self.ax.plot(df['time'], df['premium'], label='Premium', color='yellow', linestyle='--', linewidth=0.7)
        self.ax.plot(df['time'], df['discount'], label='Discount', color='pink', linestyle='--', linewidth=0.7)

    def plot_signals(self, df, buy_signals, sell_signals):
        buy_times = df['time'][buy_signals]
        sell_times = df['time'][sell_signals]

        self.ax.scatter(buy_times, df['close'][buy_signals], marker='^', color='green', label='Buy Signal', alpha=1, s=100)
        self.ax.scatter(sell_times, df['close'][sell_signals], marker='v', color='red', label='Sell Signal', alpha=1, s=100)

    def show_plot(self):
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        self.fig.autofmt_xdate()
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Price')
        self.ax.legend()
        plt.show()
        
    def plot(self, df, buy_signals, sell_signals):
        self.plot_candlestick(df)
        self.plot_indicators(df)
        self.plot_signals(df, buy_signals, sell_signals)
        self.show_plot()
