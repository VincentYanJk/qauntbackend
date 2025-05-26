import backtrader as bt

class ATR(bt.Indicator):
    lines = ('atr',)
    params = (('period', 14),)

    def __init__(self):
        self.lines.atr = bt.indicators.ATR(self.data, period=self.p.period)