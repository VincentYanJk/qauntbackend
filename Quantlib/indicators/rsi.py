import backtrader as bt

class RSI(bt.Indicator):
    lines = ('rsi',)
    params = (('period', 14),)

    def __init__(self):
        self.lines.rsi = bt.indicators.RSI(self.data, period=self.p.period)