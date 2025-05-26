from Quantlib.indicators.macd import MACD
import backtrader as bt

class MACDCrossover(bt.Strategy):
    def __init__(self):
        self.macd = MACD(self.data.close)
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if self.crossover > 0:
            self.buy()
        elif self.crossover < 0:
            self.sell()