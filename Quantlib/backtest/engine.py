import backtrader as bt
import pandas as pd

class SignalRecorder(bt.Analyzer):
    def __init__(self):
        self.trades = []

    def notify_trade(self, trade):
        if trade.isclosed:
            self.trades.append({
                'datetime': self.strategy.data.datetime.datetime(0),
                'price': trade.price,
                'size': trade.size,
                'pnl': trade.pnl
            })

    def get_analysis(self):
        return pd.DataFrame(self.trades)

def run_backtest(strategy_class, data_path, cash=100000, plot=False, kwargs=None):
    """
    Run backtest with strategy parameters
    
    Args:
        strategy_class: Strategy class to run
        data_path: Path to data file
        cash: Initial cash amount
        plot: Whether to plot results
        kwargs: Additional strategy parameters
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
    
    # Add strategy with parameters if provided
    if kwargs is not None:
        cerebro.addstrategy(strategy_class, **kwargs)
    else:
        cerebro.addstrategy(strategy_class)
        
    cerebro.broker.set_cash(cash)
    cerebro.addanalyzer(SignalRecorder, _name='signals')

    result = cerebro.run()
    strat = result[0]

    equity = cerebro.broker.get_value()
    values = [cash + v["pnl"] for v in strat.analyzers.signals.trades]
    dates = [v['datetime'] for v in strat.analyzers.signals.trades]
    trades_df = strat.analyzers.signals.get_analysis()
    
    if len(dates) > 0:
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
    df['equity'] = equity_curve.reindex(index=df.index).fillna(method='ffill')
    df['buy_signal'] = df['equity'].diff().apply(lambda x: df['close'] if x > 0 else None)
    df['sell_signal'] = df['equity'].diff().apply(lambda x: df['close'] if x < 0 else None)

    return df, trades_df