import backtrader as bt

class TrendFollowing(bt.Strategy):
    params = (("sma_period", 50), ("trade_size", 1.0))

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_period)

    def next(self):
        if not self.position and self.data.close > self.sma:
            self.buy(size=self.params.trade_size)
        elif self.position and self.data.close < self.sma:
            self.sell(size=self.params.trade_size)