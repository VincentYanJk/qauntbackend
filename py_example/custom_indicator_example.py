import backtrader as bt
import pandas as pd
from Quantlib.indicators.my_custom_factor import MyCustomFactor
from Quantlib.data.processor import preprocess_btc_csv

class CustomFactorStrategy(bt.Strategy):
    def __init__(self):
        self.custom = MyCustomFactor(self.data)

    def next(self):
        if not self.position and self.custom[0] < self.data.close[0]:
            self.buy()
        elif self.position and self.custom[0] > self.data.close[0]:
            self.sell()

df = preprocess_btc_csv("data/BTCUSDT.csv")

data = bt.feeds.PandasData(dataname=df)
cerebro = bt.Cerebro()
cerebro.addstrategy(CustomFactorStrategy)
cerebro.adddata(data)
cerebro.run()
cerebro.plot()