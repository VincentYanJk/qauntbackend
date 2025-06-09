"""
Multi-Filter Strategy Implementation
Combines multiple technical indicators for signal generation:
1. Momentum: 5-day momentum must be positive
2. Trend: Price must be above 20-day SMA
3. Volume: Current volume must be above 10-day average volume
4. Volatility: 14-day ATR must be < 5% of current price
5. Oscillator: 14-day RSI must be below 70
"""
from .base_strategy import BaseStrategy
import backtrader as bt

class MultiFilterStrategy(BaseStrategy):
    params = (
        ('momentum_period', 5),      # Momentum lookback period
        ('sma_period', 20),          # SMA period for trend filter
        ('volume_period', 10),       # Volume MA period
        ('atr_period', 14),          # ATR period
        ('atr_threshold', 0.05),     # ATR threshold as % of price
        ('rsi_period', 14),          # RSI period
        ('rsi_threshold', 70),       # RSI overbought threshold
        ('trade_size', 1.0),         # Position size as fraction of portfolio
    )

    def setup_indicators(self):
        # Momentum indicator (current close - close n periods ago)
        self.momentum = self.data.close - self.data.close(-self.params.momentum_period)
        
        # Trend filter - Simple Moving Average
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close,
            period=self.params.sma_period
        )
        
        # Volume filter - Volume Moving Average
        self.volume_ma = bt.indicators.SimpleMovingAverage(
            self.data.volume,
            period=self.params.volume_period
        )
        
        # Volatility filter - Average True Range
        self.atr = bt.indicators.AverageTrueRange(
            self.data,
            period=self.params.atr_period
        )
        
        # Oscillator - Relative Strength Index
        self.rsi = bt.indicators.RelativeStrengthIndex(
            self.data.close,
            period=self.params.rsi_period
        )
        
        # Previous position tracking
        self.prev_position = 0  # 0: no position, 1: long position

    def next(self):
        # Check all conditions for entry
        momentum_signal = self.momentum[0] > 0
        trend_signal = self.data.close[0] > self.sma[0]
        volume_signal = self.data.volume[0] > self.volume_ma[0]
        volatility_signal = self.atr[0] < (self.data.close[0] * self.params.atr_threshold)
        rsi_signal = self.rsi[0] < self.params.rsi_threshold
        
        # All conditions must be met for a buy signal
        should_be_in_position = (
            momentum_signal and
            trend_signal and
            volume_signal and
            volatility_signal and
            rsi_signal
        )
        
        # Log conditions for debugging (optional)
        if self.position.size == 0:  # Only log when not in position
            self.log(f'Signals - Momentum: {momentum_signal}, Trend: {trend_signal}, '
                    f'Volume: {volume_signal}, Volatility: {volatility_signal}, '
                    f'RSI: {rsi_signal}')
        
        # Execute trades based on signals
        if should_be_in_position and not self.position:
            self.execute_buy()
            self.prev_position = 1
            
        # Exit position if any condition becomes false
        elif not should_be_in_position and self.position:
            self.execute_sell()
            self.prev_position = 0 