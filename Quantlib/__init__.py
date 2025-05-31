"""
Main Quantlib package initialization
"""
from .backtest import run_backtest, PerformanceAnalyzer
from .strategies import (
    SMACrossover,
    RSIReversion, 
    BollingerBand,
    MACDCrossover,
    MLSignalStrategy
)
from .forecast import load_model, train_model
from .visualization import plot_equity_curve
from .data import preprocess_btc_csv, DataProcessor

__all__ = [
    'run_backtest',
    'PerformanceAnalyzer',
    'SMACrossover',
    'RSIReversion',
    'BollingerBand',
    'MACDCrossover', 
    'MLSignalStrategy',
    'load_model',
    'train_model',
    'plot_equity_curve',
    'preprocess_btc_csv',
    'DataProcessor'
]