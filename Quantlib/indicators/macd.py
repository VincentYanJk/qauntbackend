import backtrader as bt

class MACD(bt.Indicator):
    lines = ('macd', 'signal', 'hist')
    params = (('fast', 12), ('slow', 26), ('signal_period', 9))

    def __init__(self):
        macd = bt.indicators.MACD(self.data, period_me1=self.p.fast, period_me2=self.p.slow, period_signal=self.p.signal_period)
        self.lines.macd = macd.macd
        self.lines.signal = macd.signal
        self.lines.hist = macd.histo