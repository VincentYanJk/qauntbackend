import backtrader as bt

class Mean(bt.Indicator):
    lines = ('mean',)
    params = (('period', 20),)

    def __init__(self):
        self.lines.mean = bt.indicators.Mean(self.data, period=self.p.period)