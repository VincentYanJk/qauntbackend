import backtrader as bt

class SMACrossover(bt.Strategy):
    params = (
        ("short_period", 10),
        ("long_period", 30),
    )

    def __init__(self):
        self.sma1 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.sma2 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)
        self.crossover = bt.ind.CrossOver(self.sma1, self.sma2)

    def next(self):
        print(self.data.datetime.date(0), self.data.close[0], self.crossover[0])
        if self.crossover > 0:
            self.buy()
        elif self.crossover < 0:
            self.sell()