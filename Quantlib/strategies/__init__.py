"""
Trading strategies module initialization
"""
from .ml_signal_strategy import MLSignalStrategy
from .sma_crossover import SMACrossover
from .rsi_reversion import RSIReversion
from .macd_crossover import MACDCrossover
from .bollinger_band import BollingerBand
from .buy_and_hold import BuyAndHoldStrategy

__all__ = [
    'MLSignalStrategy',
    'SMACrossover',
    'RSIReversion',
    'MACDCrossover', 
    'BollingerBand',
    'BuyAndHoldStrategy'
]