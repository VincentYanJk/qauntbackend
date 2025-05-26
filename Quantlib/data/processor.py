import pandas as pd
import numpy as np
import backtrader as bt
from Quantlib.indicators.sma import SMA
from Quantlib.indicators.stddev import StdDev

def load_and_clean(filepath):
    df = pd.read_csv(filepath)
    df.dropna(inplace=True)
    df = df[df['close'] > 0]
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.sort_values('datetime', inplace=True)
    return df

class PreprocessStrategy(bt.Strategy):
    params = (('sma_period_short', 10), ('sma_period_long', 30), ('vol_period', 10),)

    def __init__(self):
        self.sma_10 = SMA(self.data.close, period=self.p.sma_period_short)
        self.sma_30 = SMA(self.data.close, period=self.p.sma_period_long)
        self.volatility = StdDev(self.data.close, period=self.p.vol_period)

    def next(self):
        pass  # Just calculate indicators, results will be collected later

def preprocess_btc_csv(filepath, output_path=None):
    df = load_and_clean(filepath)
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))

    class PandasData(bt.feeds.PandasData):
        datetime = None
        openinterest = -1

    cerebro = bt.Cerebro(stdstats=False)
    data = PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.addstrategy(PreprocessStrategy)
    cerebro.run()

    strat = cerebro.runstrats[0][0]
    df["sma_10"] = strat.sma_10.array
    df["sma_30"] = strat.sma_30.array
    df["sma_ratio"] = df["sma_10"] / df["sma_30"]
    df["volatility"] = strat.volatility.array

    if output_path:
        df.to_csv(output_path, index=False)
    return df