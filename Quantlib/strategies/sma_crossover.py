import backtrader as bt

class SMACrossover(bt.Strategy):
    params = (
        ("short_period", 10),
        ("long_period", 30),
    )

    def __init__(self):
        self.sma1 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.sma2 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)

    def next(self):
        if not self.position:
            if self.sma1[0] > self.sma2[0]:
                self.buy()
        else:
            if self.sma1[0] < self.sma2[0]:
                self.sell()