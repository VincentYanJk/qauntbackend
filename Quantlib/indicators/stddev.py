import backtrader as bt

class StdDev(bt.Indicator):
    lines = ('std',)
    params = (('period', 20),)

    def __init__(self):
        self.lines.std = bt.indicators.StdDev(self.data, period=self.p.period)