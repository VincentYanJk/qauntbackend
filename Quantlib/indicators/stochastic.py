import backtrader as bt

class Stochastic(bt.Indicator):
    lines = ('percK', 'percD')
    params = (('period', 14), ('period_dfast', 3), ('period_dslow', 3))

    def __init__(self):
        stochastic = bt.indicators.Stochastic(
            self.data, period=self.p.period,
            period_dfast=self.p.period_dfast,
            period_dslow=self.p.period_dslow
        )
        self.lines.percK = stochastic.percK
        self.lines.percD = stochastic.percD