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

def run_backtest(strategy_class, data_path, cash=100000, plot=False):

  
    df = pd.read_csv(data_path, parse_dates=["datetime"])
    df.columns = [col.strip().lower() for col in df.columns]
    print(df.columns)
    # df.set_index("datetime", inplace=True)
    df = df.sort_values(by="datetime")


    class PandasData(bt.feeds.PandasData):
        datetime = None
        openinterest = -1

    # data = PandasData(dataname=df)
    data = bt.feeds.PandasData(
    dataname=df,
    datetime='datetime',
    open='open',
    high='high',
    low='low',
    close='close',
    volume='volume',
    openinterest=None
)
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.adddata(data)
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
        print("")
        if df.index[0] == dates[0]:
            # 避免 index 重复
            equity_curve = pd.Series(values, index=dates).sort_index()
        else:
            equity_curve = pd.Series(
                [cash] + values,
                index=[df.index[0]] + dates
            ).sort_index()    
    else:
        equity_curve = pd.Series([cash], index=[df.index[0]])
    # equity_curve = pd.Series([cash] + values, index=[df.index[0]] + dates).sort_index()
    df['equity'] = equity_curve.reindex(df.index).fillna(method='ffill')
    df['buy_signal'] = df['equity'].diff().apply(lambda x: df['close'] if x > 0 else None)
    df['sell_signal'] = df['equity'].diff().apply(lambda x: df['close'] if x < 0 else None)

    return df, trades_df