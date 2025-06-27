"""
Trading strategies module initialization
"""
from .ml_signal_strategy import MLSignalStrategy
from .sma_crossover import SMACrossover
from .rsi_reversion import RSIReversion
from .macd_crossover import MACDCrossover
from .bollinger_band import BollingerBand
from .buy_and_hold import BuyAndHoldStrategy
from .momentum_sma_strategy import MomentumSMAStrategy
from .momentum_vol_rsi_strategy import MomentumVolRSIStrategy

__all__ = [
    'MLSignalStrategy',
    'SMACrossover',
    'RSIReversion',
    'MACDCrossover', 
    'BollingerBand',
    'BuyAndHoldStrategy',
    'MomentumSMAStrategy',
    'MomentumVolRSIStrategy'
]