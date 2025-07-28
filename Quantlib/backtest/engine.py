import backtrader as bt
import pandas as pd
import numpy as np
from .metrics import PerformanceAnalyzer

class SignalRecorder(bt.Analyzer):
    def __init__(self):
        super(SignalRecorder, self).__init__()
        self.trades = []
        self.current_buy = None
        self.open_trade = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            # Calculate commission based on trade value
            trade_value = order.executed.price * abs(order.executed.size)
            commission = order.executed.comm  # Commission is already calculated by backtrader based on trade value
            
            trade_record = {
                'datetime': self.strategy.datetime.datetime(0),
                'price': order.executed.price,
                'size': abs(order.executed.size),
                'commission': commission,  # Use actual commission for this trade
                'type': 'buy' if order.isbuy() else 'sell'
            }

            if order.isbuy():
                self.current_buy = trade_record
            else:  # Sell order
                if self.current_buy is not None:
                    # Calculate P&L for the buy trade
                    buy_value = self.current_buy['price'] * self.current_buy['size']
                    sell_value = order.executed.price * abs(order.executed.size)
                    
                    # For buy trade, PNL is unrealized until sell
                    buy_pnl = 0  # Buy trade has no realized PNL at the time of buying
                    # For sell trade, PNL is the difference between sell and buy values
                    sell_pnl = sell_value - buy_value
                    
                    # Update buy trade with P&L info
                    self.current_buy.update({
                        'pnl': buy_pnl,  # No realized PNL at buy time
                        'commission': self.current_buy['commission'],  # Keep original buy commission
                        'pnlcomm': buy_pnl - self.current_buy['commission'],  # Only commission as cost at buy time
                        'signal': 1  # Add signal value for buy
                    })
                    self.trades.append(self.current_buy)
                    
                    # Record sell trade with its own P&L info and commission
                    trade_record.update({
                        'pnl': sell_pnl,  # Realized PNL at sell time
                        'commission': commission,  # Use actual sell commission
                        'pnlcomm': sell_pnl - commission,  # Sell trade's pnlcomm includes the realized PNL minus its commission
                        'signal': -1  # Add signal value for sell
                    })
                    self.trades.append(trade_record)
                    
                    # Reset current buy
                    self.current_buy = None

    def notify_trade(self, trade):
        if trade.isclosed:
            # For buy-and-hold strategy handling
            if len(self.trades) == 0 and hasattr(self.strategy, 'entry_date'):
                self.trades[-1]['datetime'] = self.strategy.entry_date
        elif trade.isopen:
            self.open_trade = trade

    def stop(self):
        # Handle open trades at the end of the backtest
        if self.open_trade is not None and self.open_trade.size != 0:
            # Calculate PnL for the open position using last close price
            close_price = self.strategy.data.close[0]
            size = abs(self.open_trade.size)
            value = close_price * size
            cost = self.open_trade.value
            pnl = value - cost
            commission = self.open_trade.commission
            
            # Get the trade datetime from the strategy
            trade_datetime = self.strategy.datetime.datetime(0)
            
            # If this is a buy-and-hold strategy, use the entry date
            if hasattr(self.strategy, 'entry_date'):
                trade_datetime = self.strategy.entry_date
            
            self.trades.append({
                'datetime': trade_datetime,
                'price': close_price,
                'size': size,
                'pnl': pnl,
                'commission': commission,
                'pnlcomm': pnl - commission,
                'type': 'buy' if self.open_trade.size > 0 else 'sell',
                'signal': 1 if self.open_trade.size > 0 else -1
            })

    def get_analysis(self):
        if not self.trades:
            return pd.DataFrame(columns=['datetime', 'price', 'size', 'pnl', 'commission', 'pnlcomm', 'type', 'signal'])
        return pd.DataFrame(self.trades)

class PerformanceSummary:
    def __init__(self, metrics):
        self.initial_capital = metrics['initial_capital']
        self.final_capital = metrics['final_capital']
        self.total_return = metrics['total_return']
        self.sharpe_ratio = metrics['sharpe_ratio']
        self.max_drawdown = metrics['max_drawdown']
        self.total_trades = metrics['total_trades']
        self.win_rate = metrics['win_rate']
        self.avg_profit = metrics['avg_profit']
        self.avg_loss = metrics['avg_loss']
        self.total_commission = metrics['total_commission']
    
    def print_all(self):
        print("\n=== Performance Summary ===")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Capital: ${self.final_capital:,.2f}")
        print(f"Total Return: {self.total_return:.2%}")
        print(f"Sharpe Ratio: {self.sharpe_ratio:.4f}")
        print(f"Maximum Drawdown: {self.max_drawdown:.2%}")
        print(f"Total Trades: {self.total_trades}")
        print(f"Win Rate: {self.win_rate:.2%}")
        print(f"Average Profit: ${self.avg_profit:.2f}")
        print(f"Average Loss: ${self.avg_loss:.2f}")
        print(f"Total Commission Paid: ${self.total_commission:.2f}")
        print("========================\n")

def run_backtest(strategy_class, data_path, cash=100000, plot=False, kwargs=None):
    """
    Run backtest with strategy parameters
    
    Args:
        strategy_class: Strategy class to run
        data_path: Path to data file
        cash: Initial cash amount
        plot: Whether to plot results
        kwargs: Additional strategy parameters including:
            - trade_size: Position size as fraction of portfolio
            - commission_scheme: Dictionary with commission settings
            - slippage_scheme: Dictionary with slippage settings
            
    Returns:
        tuple: (df, trades_df, performance_summary) where:
            - df: DataFrame with backtest results
            - trades_df: DataFrame with trade details
            - performance_summary: PerformanceSummary object containing metrics
    """
    df = pd.read_csv(data_path)
    df.columns = [col.strip().lower() for col in df.columns]
    # print(df.columns)
    
    # Convert datetime column
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values(by="datetime")

    # Create PandasData feed with explicit datetime column
    data = bt.feeds.PandasData(
        dataname=df,
        datetime='datetime',  # Specify datetime column
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=-1
    )
    
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.adddata(data)
    
    # Extract broker settings from kwargs
    if kwargs is None:
        kwargs = {}
    
    # Handle broker settings first
    if 'commission_scheme' in kwargs:
        comm_scheme = kwargs.pop('commission_scheme')
        cerebro.broker.setcommission(**comm_scheme)
    
    if 'slippage_scheme' in kwargs:
        slip_scheme = kwargs.pop('slippage_scheme')
        if 'slip_perc' in slip_scheme:
            cerebro.broker.set_slippage_perc(slip_scheme['slip_perc'])
        if 'slip_fixed' in slip_scheme:
            cerebro.broker.set_slippage_fixed(slip_scheme['slip_fixed'])
    
    # Add strategy with remaining parameters
    cerebro.addstrategy(strategy_class, **kwargs)
    
    cerebro.broker.set_cash(cash)
    cerebro.addanalyzer(SignalRecorder, _name='signals')

    result = cerebro.run()
    strat = result[0]

    equity = cerebro.broker.get_value()
    trades_df = strat.analyzers.signals.get_analysis()
    trades_df.to_csv('data/trades_df.csv')
    if len(trades_df) > 0:
        # For buy-and-hold strategies, we need to handle the equity curve differently
        if len(trades_df) == 1:  # Likely a buy-and-hold strategy
            df.set_index('datetime', inplace=True)
            
            # Get the trade details and ensure all values are float
            position_size = float(trades_df['size'].iloc[0])  # Number of BTC
            entry_date = pd.to_datetime(trades_df['datetime'].iloc[0])  # This should be 2014-12-02
            entry_price = float(trades_df['price'].iloc[0])  # This should be $378.39
            commission = float(trades_df['commission'].iloc[0])
            
            # Print debug info
            print("\nBuy & Hold Debug Info:")
            print(f"Position Size: {position_size}")
            print(f"Entry Date: {entry_date}")
            print(f"Entry Price: ${entry_price:,.2f}")
            print(f"Commission: ${commission:,.2f}")
            print(f"Initial Cost: ${entry_price * position_size + commission:,.2f}")
            
            # Create equity curve
            df['equity'] = pd.Series(index=df.index, dtype=float)  # Initialize empty series with float type
            
            # Before entry date, equity is initial cash
            df.loc[df.index < entry_date, 'equity'] = float(cash)
            
            # After entry date, equity is position value + remaining cash
            mask = df.index >= entry_date
            df.loc[mask, 'equity'] = df.loc[mask, 'close'].astype(float) * position_size
            
            # Print more debug info
            # print("\nEquity Curve Sample:")
            # print(df['equity'].head())
            # print("\nEquity Curve Stats:")
            # print(f"Min: ${df['equity'].min():,.2f}")
            # print(f"Max: ${df['equity'].max():,.2f}")
            # print(f"First: ${df['equity'].iloc[0]:,.2f}")
            # print(f"Last: ${df['equity'].iloc[-1]:,.2f}")
            # print(f"\nSample dates:")
            # print(f"First date: {df.index[0]}")
            # print(f"Entry date: {entry_date}")
            # print(f"Last date: {df.index[-1]}")
            
            equity_curve = df['equity']
        else:
            # For regular strategies, calculate equity curve from trades
            df.set_index('datetime', inplace=True)
            df['equity'] = pd.Series(index=df.index)  # Initialize empty series
            df['equity'] = float(cash)  # Start with initial cash
            
            # Process each trade sequentially
            for i in range(len(trades_df)):
                trade_date = pd.to_datetime(trades_df['datetime'].iloc[i])
                trade_pnl = trades_df['pnlcomm'].iloc[i]
                df.loc[df.index >= trade_date, 'equity'] = df.loc[df.index >= trade_date, 'equity'] + float(trade_pnl)
            
            equity_curve = df['equity']
    else:
        equity_curve = pd.Series([cash], index=[df['datetime'].iloc[0]])

    df.set_index('datetime', inplace=True) if not df.index.name == 'datetime' else None
    df['equity'] = equity_curve.reindex(index=df.index).ffill()
    
    # # Generate signals
    # equity_diff = df['equity'].diff()
    
    # # Standard signal column (1/-1/0)
    # df['signal'] = 0  # Initialize with 0 (no signal)
    # df.loc[equity_diff > 0, 'signal'] = 1  # Buy signal
    # df.loc[equity_diff < 0, 'signal'] = -1  # Sell signal
    
    # # Separate buy/sell columns for plotting
    # df['buy_signal'] = None  # Initialize with None
    # df['sell_signal'] = None  # Initialize with None
    # df.loc[df['signal'] == 1, 'buy_signal'] = df.loc[df['signal'] == 1, 'close']
    # df.loc[df['signal'] == -1, 'sell_signal'] = df.loc[df['signal'] == -1, 'close']
    
    # # Store signal prices for reference
    # df['signal_price'] = None  # Initialize price column
    # df.loc[df['signal'] != 0, 'signal_price'] = df.loc[df['signal'] != 0, 'close']

    # 先生成 signal 列
    trades_df['signal'] = trades_df['type'].map({'buy': 1, 'sell': -1})

    # 把交易信号按时间合并到主行情表
    df = df.merge(trades_df[['datetime', 'signal', 'price']], on='datetime', how='left', suffixes=('', '_trade'))

    # 没信号的日期补0
    df['signal'] = df['signal'].fillna(0)

    # buy_signal/sell_signal 便于画图
    df['buy_signal'] = df.apply(lambda row: row['close'] if row['signal'] == 1 else None, axis=1)
    df['sell_signal'] = df.apply(lambda row: row['close'] if row['signal'] == -1 else None, axis=1)
    df['signal_price'] = df['price'].where(df['signal'] != 0)



    # Calculate performance metrics using PerformanceAnalyzer
    if len(trades_df) == 1:  # For buy-and-hold strategy, get the actual final value
        initial_value = cash
        final_value = float(equity)  # Use the broker's final portfolio value
    else:
        initial_value = cash
        final_value = df['equity'].iloc[-1]  # Use the last value from the equity curve
    
    total_return = (final_value - initial_value) / initial_value

    # Get returns for Sharpe ratio calculation
    returns = df['equity'].pct_change().dropna()
    
    # Use PerformanceAnalyzer for calculations
    analyzer = PerformanceAnalyzer()
    sharpe_ratio = analyzer.sharpe_ratio(returns)  # Uses 365 days and 2% risk-free rate
    max_drawdown = analyzer.max_drawdown(df['equity'])

    # Calculate trading statistics
    total_trades = len(trades_df)
    if total_trades > 0:
        profitable_trades = len(trades_df[trades_df['pnlcomm'] > 0])
        win_rate = profitable_trades / total_trades if total_trades > 1 else 1.0  # For buy-and-hold, count as 100% if profitable
        avg_won = final_value - initial_value if total_trades == 1 else trades_df[trades_df['pnlcomm'] > 0]['pnlcomm'].mean()  # For buy-and-hold, use total profit
        avg_lost = trades_df[trades_df['pnlcomm'] < 0]['pnlcomm'].mean() if len(trades_df[trades_df['pnlcomm'] < 0]) > 0 else 0
        total_commission = trades_df['commission'].sum()
    else:
        profitable_trades = 0
        win_rate = 0
        avg_won = 0
        avg_lost = 0
        total_commission = 0

    # Create performance summary object
    performance_summary = PerformanceSummary(metrics={
        'initial_capital': initial_value,
        'final_capital': final_value,
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'avg_profit': avg_won,
        'avg_loss': avg_lost,
        'total_commission': total_commission
    })

    return df, trades_df, performance_summary

def run_buy_and_hold(self, df, cash):
    """Run a buy and hold strategy."""
    trades = []
    
    # Place buy order on the first day
    entry_price = df['close'].iloc[0]
    position_size = (cash * 0.998) / entry_price  # Leave some cash for commission
    commission = cash * 0.002  # 0.2% commission
    
    # Record the trade
    trade = {
        'datetime': df['datetime'].iloc[0],  # Use the first date
        'price': entry_price,
        'size': position_size,
        'pnl': (df['close'].iloc[-1] - entry_price) * position_size,
        'commission': commission,
        'pnlcomm': (df['close'].iloc[-1] - entry_price) * position_size - commission
    }
    trades.append(trade)
    
    # Convert to DataFrame
    trades_df = pd.DataFrame(trades)
    
    # Calculate final portfolio value
    final_value = position_size * df['close'].iloc[-1] + (cash - position_size * entry_price - commission)
    print(f"{df['datetime'].iloc[-1]} Buy and Hold Final Portfolio Value: ${final_value:.2f}")
    
    return trades_df