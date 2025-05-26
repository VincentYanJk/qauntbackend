import backtrader as bt

class TrendFollowing(bt.Strategy):
    params = (("sma_period", 50),)

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_period)

    def next(self):
        if not self.position and self.data.close > self.sma:
            self.buy()
        elif self.position and self.data.close < self.sma:
            self.sell()