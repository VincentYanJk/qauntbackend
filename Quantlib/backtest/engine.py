import backtrader as bt
import pandas as pd
import numpy as np
from .metrics import PerformanceAnalyzer

class SignalRecorder(bt.Analyzer):
    def __init__(self):
        self.trades = []
        super().__init__()

    def notify_trade(self, trade):
        if trade.isclosed:
            self.trades.append({
                'datetime': self.strategy.data.datetime.datetime(0),
                'price': trade.price,
                'size': trade.size,
                'pnl': trade.pnl,
                'commission': trade.commission,
                'pnlcomm': trade.pnlcomm
            })

    def get_analysis(self):
        if not self.trades:
            return pd.DataFrame(columns=['datetime', 'price', 'size', 'pnl', 'commission', 'pnlcomm'])
        return pd.DataFrame(self.trades)

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
    """
    df = pd.read_csv(data_path)
    df.columns = [col.strip().lower() for col in df.columns]
    print(df.columns)
    
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
    
    if len(trades_df) > 0:
        values = [cash + trades_df['pnlcomm'].cumsum().iloc[i] for i in range(len(trades_df))]
        dates = trades_df['datetime'].tolist()
        
        if dates[0] == df['datetime'].iloc[0]:
            equity_curve = pd.Series(values, index=dates)
        else:
            equity_curve = pd.Series(
                [cash] + values,
                index=[df['datetime'].iloc[0]] + dates
            )
    else:
        equity_curve = pd.Series([cash], index=[df['datetime'].iloc[0]])

    df.set_index('datetime', inplace=True)
    df['equity'] = equity_curve.reindex(index=df.index).ffill()
    df['buy_signal'] = df['equity'].diff().apply(lambda x: df['close'] if x > 0 else None)
    df['sell_signal'] = df['equity'].diff().apply(lambda x: df['close'] if x < 0 else None)

    # Calculate performance metrics
    initial_value = cash
    final_value = df['equity'].iloc[-1]
    total_return = (final_value - initial_value) / initial_value

    # Calculate Sharpe Ratio
    returns = df['equity'].pct_change().dropna()
    sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std()) if len(returns) > 0 and returns.std() != 0 else 0

    # Calculate Maximum Drawdown
    cummax = df['equity'].cummax()
    drawdown = (df['equity'] - cummax) / cummax
    max_drawdown = drawdown.min()

    # Calculate trading statistics
    total_trades = len(trades_df)
    if total_trades > 0:
        profitable_trades = len(trades_df[trades_df['pnlcomm'] > 0])
        win_rate = profitable_trades / total_trades
        avg_won = trades_df[trades_df['pnlcomm'] > 0]['pnlcomm'].mean() if profitable_trades > 0 else 0
        avg_lost = trades_df[trades_df['pnlcomm'] < 0]['pnlcomm'].mean() if len(trades_df[trades_df['pnlcomm'] < 0]) > 0 else 0
        total_commission = trades_df['commission'].sum()
    else:
        profitable_trades = 0
        win_rate = 0
        avg_won = 0
        avg_lost = 0
        total_commission = 0

    # Print performance summary
    print("\n=== Performance Summary ===")
    print(f"Initial Capital: ${initial_value:,.2f}")
    print(f"Final Capital: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.2%}")
    print(f"Sharpe Ratio: {sharpe_ratio:.4f}")
    print(f"Maximum Drawdown: {max_drawdown:.2%}")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.2%}")
    print(f"Average Profit: ${avg_won:.2f}")
    print(f"Average Loss: ${avg_lost:.2f}")
    print(f"Total Commission Paid: ${total_commission:.2f}")
    print("========================\n")

    return df, trades_df