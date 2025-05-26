import backtrader as bt

class CrossOver(bt.Indicator):
    lines = ('crossover',)

    def __init__(self, line1, line2):
        self.lines.crossover = bt.indicators.CrossOver(line1, line2)