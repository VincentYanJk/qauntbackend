from Quantlib.indicators.macd import MACD
import backtrader as bt

class MACDCrossover(bt.Strategy):
    params = (("trade_size", 1.0),)

    def __init__(self):
        self.macd = MACD(self.data.close)
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if self.crossover > 0:
            self.buy(size=self.params.trade_size)
        elif self.crossover < 0:
            self.sell(size=self.params.trade_size)