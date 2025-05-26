import backtrader as bt

class BollingerBands(bt.Indicator):
    lines = ('mid', 'top', 'bot')
    params = (('period', 20,), ('devfactor', 2.0,))

    def __init__(self):
        bb = bt.indicators.BollingerBands(self.data, period=self.p.period, devfactor=self.p.devfactor)
        self.lines.mid = bb.lines.mid
        self.lines.top = bb.lines.top
        self.lines.bot = bb.lines.bot