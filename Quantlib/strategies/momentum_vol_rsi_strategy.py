"""
Momentum-Volume-RSI Strategy Implementation
Combines three technical indicators:
1. Momentum: 5-day momentum (current close minus close 5 days ago)
2. Volume Ratio: (5-day avg volume) / (10-day avg volume) - 1
3. RSI: 14-day Relative Strength Index
"""
from .base_strategy import BaseStrategy
import backtrader as bt

class MomentumVolRSIStrategy(BaseStrategy):
    params = (
        ('momentum_period', 5),       # Momentum lookback period
        ('vol_short_period', 5),      # Short-term volume MA period
        ('vol_long_period', 10),      # Long-term volume MA period
        ('rsi_period', 14),          # RSI period
        ('momentum_threshold', 0),    # Momentum threshold for buy signal
        ('vol_ratio_threshold', 0),   # Volume ratio threshold for buy signal
        ('rsi_lower', 30),           # RSI oversold threshold
        ('rsi_upper', 70),           # RSI overbought threshold
        ('trade_size', 1.0),         # Position size as fraction of portfolio
    )

    def setup_indicators(self):
        # Momentum indicator (current close - close n periods ago)
        self.momentum = self.data.close - self.data.close(-self.params.momentum_period)
        
        # Volume Moving Averages for volume ratio
        self.vol_short = bt.indicators.SimpleMovingAverage(
            self.data.volume,
            period=self.params.vol_short_period
        )
        self.vol_long = bt.indicators.SimpleMovingAverage(
            self.data.volume,
            period=self.params.vol_long_period
        )
        
        # Volume ratio calculation
        self.vol_ratio = (self.vol_short / self.vol_long) - 1
        
        # RSI indicator
        self.rsi = bt.indicators.RelativeStrengthIndex(
            self.data.close,
            period=self.params.rsi_period
        )
        
        # Previous position tracking
        self.prev_position = 0  # 0: no position, 1: long position

    def next(self):
        # Calculate signals
        momentum_signal = self.momentum[0] > self.params.momentum_threshold
        vol_ratio_signal = self.vol_ratio[0] > self.params.vol_ratio_threshold
        
        # RSI conditions
        rsi_buy_signal = self.rsi[0] < self.params.rsi_lower  # Oversold condition
        rsi_sell_signal = self.rsi[0] > self.params.rsi_upper  # Overbought condition
        
        # Entry conditions
        should_buy = (
            momentum_signal and      # Positive momentum
            vol_ratio_signal and     # Increasing volume
            rsi_buy_signal          # Oversold RSI
        )
        
        # Exit conditions
        should_sell = (
            not momentum_signal or   # Negative momentum
            not vol_ratio_signal or  # Decreasing volume
            rsi_sell_signal         # Overbought RSI
        )
        
        # Log conditions for debugging (optional)
        if self.position.size == 0:  # Only log when not in position
            self.log(f'Signals - Momentum: {momentum_signal}, Vol Ratio: {vol_ratio_signal:.3f}, '
                    f'RSI: {self.rsi[0]:.1f}')
        
        # Execute trades based on signals
        if should_buy and not self.position:
            self.execute_buy()
            self.prev_position = 1
            
        elif should_sell and self.position:
            self.execute_sell()
            self.prev_position = 0 