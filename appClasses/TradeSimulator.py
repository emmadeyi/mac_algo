import pandas as pd
import json
import datetime

class TradingSimulator:
    def __init__(self, equity=2.0, commission=0.001, max_lot_size=0.1, partial_tp_percentage=0.5, pip_location=0.0001, max_profit=50, max_loss=-0.5, sl_pips=5, tp_pips=50, min_equity=0):
        self.equity = equity
        self.initial_equity = equity
        self.commission = commission
        self.max_lot_size = max_lot_size
        self.partial_tp_percentage = partial_tp_percentage
        self.orders = []
        self.closed_orders = []
        self.pip_location = pip_location
        self.start_time = None
        self.end_time = None
        self.total_duration = pd.Timedelta(0)
        self.last_price = 0
        self.max_profit = max_profit #in usd
        self.max_loss = max_loss #in usd
        self.sl_pips = sl_pips
        self.tp_pips = tp_pips
        self.min_equity = min_equity
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


    def place_order(self, order_type, price, time, sl_pips=None, tp_pips=None, lot_size=1.0):
        if lot_size > self.max_lot_size:
            lot_size = self.max_lot_size
        
        # Calculate SL and TP prices based on pips
        sl_price = price - sl_pips * self.pip_location if order_type == 'buy' else price + sl_pips * self.pip_location
        tp_price = price + tp_pips * self.pip_location if order_type == 'buy' else price - tp_pips * self.pip_location
        
        order = {
            'type': order_type,
            'open_price': price,
            'open_time': time,
            'sl': sl_price,
            'tp': tp_price,
            'lot_size': lot_size,
            'status': 'open',
            'close_price': None,
            'close_time': None,
            'duration': None,
            'pnl': 0,
            'pip_difference': 0,
            'commission': round((price * self.commission * lot_size), 7)
        }
        self.orders.append(order)
        print(f"Placed {order_type} order at {price} with lot size {lot_size} at {time}")

    def close_order(self, order, close_price, close_time):
        order['close_price'] = close_price
        order['close_time'] = close_time
        order['pip_difference'] = (close_price - order['open_price']) / self.pip_location if order['type'] == 'buy' else (order['open_price'] - close_price) / self.pip_location
        order['pnl'] = order['pip_difference'] * order['lot_size'] - order['commission']
        order['status'] = 'closed'
        order['duration'] = order['close_time'] - order['open_time']
        self.total_duration += order['duration']
        self.closed_orders.append(order)
        self.orders.remove(order)
        self.equity += order['pnl']
        print(f"Closed {order['type']} order at {close_price} at {close_time}, PnL: {round(order['pnl'], 7)}, Duration: {order['duration']}, Equity: {round(self.equity, 7)}")

    def manage_orders(self, current_price, current_time):
        self.last_price = current_price
        for order in self.orders[:]:
            # Check stop loss
            if order['sl'] and ((order['type'] == 'buy' and current_price <= order['sl']) or 
                                (order['type'] == 'sell' and current_price >= order['sl'])):
                print(f"SL hit for {order['type']} order at {current_price}")
                self.close_order(order, current_price, current_time)
                continue
            
            # Check take profit
            if order['tp'] and ((order['type'] == 'buy' and current_price >= order['tp']) or 
                                (order['type'] == 'sell' and current_price <= order['tp'])):
                print(f"TP hit for {order['type']} order at {current_price}")
                self.close_order(order, current_price, current_time)
                continue
            
            # Calculate current PnL
            pip_difference = (current_price - order['open_price']) / self.pip_location if order['type'] == 'buy' else (order['open_price'] - current_price) / self.pip_location
            current_pnl = pip_difference * order['lot_size'] - order['commission']

            # Check if equity is below minimum threshold
            if self.equity <= self.min_equity:
                print("Equity depleted. Stopping simulation.")
                return

            # Check max profit
            if current_pnl >= self.max_profit:
                print(f"Max profit hit for {order['type']} order at {current_price}, PnL: {round(current_pnl, 5)}")
                self.close_order(order, current_price, current_time)
                continue

            # Check max loss
            if current_pnl <= self.max_loss:
                print(f"Max loss hit for {order['type']} order at {current_price}, PnL: {round(current_pnl, 5)}")
                self.close_order(order, current_price, current_time)
                continue

    def get_signals(self, df):
        signals = []
        for i in range(1, len(df)):
            if df['close'][i] > df['ma'][i] and df['close'][i - 1] <= df['ma'][i - 1]:
                signals.append('buy')
            elif df['close'][i] < df['ma'][i] and df['close'][i - 1] >= df['ma'][i - 1]:
                signals.append('sell')
            else:
                signals.append('')
        signals.append('')  # Append empty string for the last candle
        return signals

    def close_all_orders(self, current_price, current_time):
        for order in self.orders[:]:
            self.close_order(order, current_price, current_time)

    def backtest(self, df):
        # Initialize start time with the first timestamp in the DataFrame
        self.start_time = df['time'].iloc[0]
        for i in range(1, len(df)):

            self.manage_orders(df['close'][i], df['time'][i])
            if df['signals'][i] == 'buy':
                # Close all sell orders before placing a buy order
                if any(order['type'] == 'sell' for order in self.orders):
                    self.close_all_orders(df['close'][i], df['time'][i])
                self.place_order('buy', df['close'][i], df['time'][i], self.sl_pips, self.tp_pips)  # Example SL and TP levels in pips
            elif df['signals'][i] == 'sell':
                # Close all buy orders before placing a sell order
                if any(order['type'] == 'buy' for order in self.orders):
                    self.close_all_orders(df['close'][i], df['time'][i])
                self.place_order('sell', df['close'][i], df['time'][i], self.sl_pips, self.tp_pips)  # Example SL and TP levels in pips
        
            # Check if equity is depleted after placing orders
            if self.equity <= self.min_equity:
                print("Equity depleted. Stopping simulation.")
                break
        
        # Set end time with the last timestamp in the DataFrame
        self.end_time = df['time'].iloc[-1]

    def backtest(self, df):
    # Initialize start time with the first timestamp in the DataFrame
        self.start_time = df['time'].iloc[0]
        
        # df['signals'] = self.get_signals(df)
        for i in range(1, len(df)):
            current_time = df['time'][i]
            current_price = df['close'][i]
            current_hour = df['time'][i].hour
            if self.is_kill_zone(current_hour):
            # if self.is_kill_zone():
                self.manage_orders(current_price, current_time)
                if df['signals'][i] == 'buy':
                    # Close all sell orders before placing a buy order
                    if any(order['type'] == 'sell' for order in self.orders):
                        self.close_all_orders(current_price, current_time)
                    self.place_order('buy', current_price, current_time, self.sl_pips, self.tp_pips)  # Example SL and TP levels in pips
                elif df['signals'][i] == 'sell':
                    # Close all buy orders before placing a sell order
                    if any(order['type'] == 'buy' for order in self.orders):
                        self.close_all_orders(current_price, current_time)
                    self.place_order('sell', current_price, current_time, self.sl_pips, self.tp_pips)  # Example SL and TP levels in pips
        
        # Set end time with the last timestamp in the DataFrame
        self.end_time = df['time'].iloc[-1]

    def results(self):
        total_trades = len(self.closed_orders)
        winning_trades = sum(1 for order in self.closed_orders if order['pnl'] > 0)
        losing_trades = total_trades - winning_trades
        winrate = winning_trades / total_trades * 100 if total_trades > 0 else 0
        max_win_pips = max((order['pip_difference'] for order in self.closed_orders), default=0)
        max_loss_pips = min((order['pip_difference'] for order in self.closed_orders), default=0)
        max_win_usd = max((order['pnl'] for order in self.closed_orders), default=0)
        max_loss_usd = min((order['pnl'] for order in self.closed_orders), default=0)
        avg_win_pips = (sum(order['pip_difference'] for order in self.closed_orders if order['pnl'] > 0) / winning_trades) if winning_trades > 0 else 0
        avg_loss_pips = (sum(order['pip_difference'] for order in self.closed_orders if order['pnl'] < 0) / losing_trades) if losing_trades > 0 else 0
        avg_win_usd = (sum(order['pnl'] for order in self.closed_orders if order['pnl'] > 0) / winning_trades) if winning_trades > 0 else 0
        avg_loss_usd = (sum(order['pnl'] for order in self.closed_orders if order['pnl'] < 0) / losing_trades) if losing_trades > 0 else 0
        
        # Calculate PnL of open orders
        open_orders_pnl = 0
        for order in self.orders:
            pip_difference = (self.last_price - order['open_price']) / self.pip_location if order['type'] == 'buy' else (order['open_price'] - self.last_price) / self.pip_location
            order_pnl = pip_difference * order['lot_size'] - order['commission']
            open_orders_pnl += order_pnl
            print(f"Open {order['type']} order PnL: {order_pnl}. Open Price: {order['open_price']}, Open Time: {order['open_time']} ")

        return {
            'Initial equity': round(self.initial_equity, 7),
            'Current equity': round(self.equity, 7),
            'pnl': round((self.equity - self.initial_equity), 7),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'winrate': f'{round(winrate, 2)}%',
            'max_win_pips': round(max_win_pips, 5),
            'max_loss_pips': round(max_loss_pips, 5),
            'max_win_usd': round(max_win_usd, 5),
            'max_loss_usd': round(max_loss_usd, 5),
            'avg_win_pips': round(avg_win_pips, 5),
            'avg_loss_pips': round(avg_loss_pips, 5),
            'avg_win_usd': round(avg_win_usd, 5),
            'avg_loss_usd': round(avg_loss_usd, 5),
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'total_duration': str(self.total_duration),
            'open_orders_pnl': round(open_orders_pnl, 7)
        }


