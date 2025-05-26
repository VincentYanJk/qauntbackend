import backtrader as bt

class WilliamsR(bt.Indicator):
    lines = ('williamsr',)
    params = (('period', 14),)

    def __init__(self):
        self.lines.williamsr = bt.indicators.WilliamsR(self.data, period=self.p.period)