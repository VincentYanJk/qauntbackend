import backtrader as bt

class EMA(bt.Indicator):
    lines = ('ema',)
    params = (('period', 20),)

    def __init__(self):
        self.lines.ema = bt.indicators.EMA(self.data, period=self.p.period)