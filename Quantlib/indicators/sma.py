import backtrader as bt

class SMA(bt.Indicator):
    lines = ('sma',)
    params = (('period', 20),)

    def __init__(self):
        self.lines.sma = bt.indicators.SMA(self.data, period=self.p.period)