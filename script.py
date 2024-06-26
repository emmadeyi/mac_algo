import MetaTrader5 as mt
from appClasses.IndicatorsClass import IndicatorsClass
from appClasses.SymbolCollectionClass import SymbolCollectionClass
from appClasses.TradeSimulator import TradingSimulator
from appClasses.PlotClass import PlotClass
import json

if __name__ == '__main__':  
    sc = SymbolCollectionClass()
    indicators = IndicatorsClass()
    symbol = 'XAUUSD'
    timeframe = mt.TIMEFRAME_H1    
    pip_location = sc.get_symbol_piplocation(symbol=symbol)
    df = sc.fetch_candles_counts(symbol, timeframe, 10000)
    short_ma = 5
    long_ma = 10
    # # # Process MA Cross
    df = indicators.moving_averages_cross(df, short_ma, long_ma, kill_zone=False)

    # # # Simulate Strategy:
    simulator = TradingSimulator(pip_location=pip_location)
    simulator.backtest(df)
    result = simulator.results()
    print(json.dumps(result, indent=4))

    print(df[(df['signals'] == 'buy') | (df['signals'] == 'sell')].count())
    # # # Plot the candlestick chart with MAs and buy/sell signals
    plotter = PlotClass(symbol=symbol, timeframe=timeframe)
    plotter.plot_mac_chart(df, short_ma, long_ma)



