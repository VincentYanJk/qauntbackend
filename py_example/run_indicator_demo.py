# 📓 Indicator Demo Strategy: RSI + SMA Crossover

from Quantlib.data.processor import preprocess_btc_csv
from Quantlib.backtest.engine import run_backtest
from Quantlib.visualization.visualize import plot_equity_curve
import backtrader as bt

from Quantlib.indicators.sma import SMA
from Quantlib.indicators.rsi import RSI

class SMARsiStrategy(bt.Strategy):
    def __init__(self):
        self.sma = SMA(self.data, period=20)
        self.rsi = RSI(self.data, period=14)

    def next(self):
        if not self.position and self.data.close[0] > self.sma[0] and self.rsi[0] < 30:
            self.buy()
        elif self.position and self.data.close[0] < self.sma[0] and self.rsi[0] > 70:
            self.sell()

df = preprocess_btc_csv("data/BTCUSDT.csv")
equity = run_backtest(
    strategy_class=SMARsiStrategy,
    data_path="data/BTCUSDT.csv",
    cash=100000,
    plot=False
)
plot_equity_curve(equity)