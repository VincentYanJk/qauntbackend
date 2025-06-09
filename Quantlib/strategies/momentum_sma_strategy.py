"""
Momentum-SMA strategy implementation
Generates buy signals when:
1. 5-day momentum is positive
2. Closing price is above 20-day SMA
"""
from .base_strategy import BaseStrategy
import backtrader as bt

class MomentumSMAStrategy(BaseStrategy):
    params = (
        ('momentum_period', 5),
        ('sma_period', 20),
        ('trade_size', 1.0),
    )

    def setup_indicators(self):
        # Calculate momentum (current close - close n periods ago)
        self.momentum = self.data.close - self.data.close(-self.params.momentum_period)
        
        # Calculate SMA
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close,
            period=self.params.sma_period
        )
        
        # Previous position tracking
        self.prev_position = 0  # 0: no position, 1: long position

    def next(self):
        # Check if we should be in a position
        should_be_in_position = (
            self.momentum[0] > 0 and  # Positive momentum
            self.data.close[0] > self.sma[0]  # Price above SMA
        )
        
        # If we should be in a position and we're not
        if should_be_in_position and not self.position:
            self.execute_buy()
            self.prev_position = 1
            
        # If we shouldn't be in a position and we are
        elif not should_be_in_position and self.position:
            self.execute_sell()
            self.prev_position = 0 