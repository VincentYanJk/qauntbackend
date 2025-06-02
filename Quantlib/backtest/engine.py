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