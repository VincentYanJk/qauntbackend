import backtrader as bt
import numpy as np

class MFI(bt.Indicator):
    """
    Money Flow Index (MFI) indicator
    Formula:
    - Typical Price = (High + Low + Close)/3
    - Raw Money Flow = Typical Price * Volume
    - Money Flow Ratio = (14-period Positive Money Flow)/(14-period Negative Money Flow)
    - Money Flow Index = 100 - 100/(1 + Money Flow Ratio)
    """
    
    lines = ('mfi',)
    params = (('period', 14),)
    
    def __init__(self):
        # We'll use the built-in typical price calculation
        self.typical_price = (self.data.high + self.data.low + self.data.close) / 3.0
        self.money_flow = self.typical_price * self.data.volume
        
        # Create a line for storing money flow values
        self.pos_flow = bt.indicators.SumN(
            bt.If(self.typical_price > self.typical_price(-1), self.money_flow, 0.0),
            period=self.p.period
        )
        
        self.neg_flow = bt.indicators.SumN(
            bt.If(self.typical_price < self.typical_price(-1), self.money_flow, 0.0),
            period=self.p.period
        )
        
        # Add a small epsilon to prevent division by zero
        epsilon = 1e-10
        
        # Calculate final MFI value
        money_ratio = self.pos_flow / (self.neg_flow + epsilon)
        self.lines.mfi = 100.0 - (100.0 / (1.0 + money_ratio)) 