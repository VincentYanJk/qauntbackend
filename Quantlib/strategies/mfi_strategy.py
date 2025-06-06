"""
MFI Strategy implementation
"""
from .base_strategy import BaseStrategy
from Quantlib.indicators.mfi import MFI
import backtrader as bt

class MFIStrategy(BaseStrategy):
    """
    Money Flow Index (MFI) Strategy
    - Buy when MFI crosses above oversold level (indicating potential reversal up)
    - Sell when MFI crosses below overbought level (indicating potential reversal down)
    """
    params = (
        ('period', 14),  # MFI period
        ('oversold', 20),  # Oversold threshold
        ('overbought', 80),  # Overbought threshold
        ('trade_size', 1.0),  # Position size
    )

    def setup_indicators(self):
        # Initialize MFI indicator
        self.mfi = MFI(self.data, period=self.params.period)
        
        # Track previous MFI values for crossover detection
        self.prev_mfi = None
        self.prev_signal = 0

    def next(self):
        # Skip if not enough data
        if len(self.mfi) < 2:
            return
            
        # Store current signal
        signal = 0
        
        # Check for oversold to non-oversold crossover (buy signal)
        if self.prev_mfi is not None:
            if (self.prev_mfi <= self.params.oversold and 
                self.mfi[0] > self.params.oversold):
                signal = 1
            # Check for overbought to non-overbought crossover (sell signal)
            elif (self.prev_mfi >= self.params.overbought and 
                  self.mfi[0] < self.params.overbought):
                signal = -1
        
        # Store current MFI for next iteration
        self.prev_mfi = self.mfi[0]
        
        # Execute trades based on signals
        if self.prev_signal == 1:
            self.execute_buy()
        elif self.prev_signal == -1:
            self.execute_sell()
            
        self.prev_signal = signal 