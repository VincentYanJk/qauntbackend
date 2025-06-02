"""
SMA Crossover strategy implementation
"""
from .base_strategy import BaseStrategy
import backtrader as bt

class SMACrossover(BaseStrategy):
    params = (
        ('short_period', 10),
        ('long_period', 30),
        ('trade_size', 1.0),
    )

    def setup_indicators(self):
        # previous day's singal
        self.prev_signal = 0
        self.sma1 = bt.indicators.SimpleMovingAverage(
            self.data.close, 
            period=self.params.short_period
        )
        self.sma2 = bt.indicators.SimpleMovingAverage(
            self.data.close, 
            period=self.params.long_period
        )
        self.crossover = bt.ind.CrossOver(self.sma1, self.sma2)

    def next(self):
        # current day single
        single = 0 
        if self.crossover > 0:
            single = 1;
            self.execute_buy()
        elif self.crossover < 0:
            single = 1;
            self.execute_sell()

        if self.prev_signal == 1:
            self.execute_buy()
            
        elif self.prev_signal == -1:
            self.execute_buy()
            


        self.prev_signal = single