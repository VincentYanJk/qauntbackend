import pandas as pd
import numpy as np
from typing import List, Dict, Any

class FeatureGenerator:
    """Feature generator for cryptocurrency data"""
    
    @staticmethod
    def returns(df: pd.DataFrame, periods: List[int] = [1, 5, 10]) -> pd.DataFrame:
        """Calculate returns over multiple periods"""
        for period in periods:
            df[f'return_{period}'] = df['close'].pct_change(period)
        return df
    
    @staticmethod
    def sma(df: pd.DataFrame, periods: List[int] = [10, 30, 50]) -> pd.DataFrame:
        """Calculate SMAs and their ratios"""
        # Calculate SMAs
        for period in periods:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
        
        # Calculate SMA ratios for adjacent periods
        for i in range(len(periods)-1):
            short_period = periods[i]
            long_period = periods[i+1]
            df[f'sma_ratio_{short_period}_{long_period}'] = (
                df[f'sma_{short_period}'] / df[f'sma_{long_period}']
            )
        return df
    
    @staticmethod
    def volatility(df: pd.DataFrame, periods: List[int] = [10, 30]) -> pd.DataFrame:
        """Calculate volatility over multiple periods"""
        for period in periods:
            df[f'volatility_{period}'] = df['return_1'].rolling(window=period).std()
        return df
    
    @staticmethod
    def rsi(df: pd.DataFrame, periods: List[int] = [14, 28]) -> pd.DataFrame:
        """Calculate RSI for multiple periods"""
        for period in periods:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        return df
    
    @staticmethod
    def volume_features(df: pd.DataFrame, periods: List[int] = [5, 10, 20]) -> pd.DataFrame:
        """Calculate volume-based features"""
        # Handle both 'Volume' and 'volume' column names
        volume_col = 'Volume' if 'Volume' in df.columns else 'volume'
        if volume_col not in df.columns:
            raise ValueError("No volume column found in data (tried both 'Volume' and 'volume')")
            
        for period in periods:
            df[f'volume_sma_{period}'] = df[volume_col].rolling(window=period).mean()
            df[f'volume_ratio_{period}'] = df[volume_col] / df[f'volume_sma_{period}']
        return df

def generate_features(df: pd.DataFrame, feature_config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Generate features based on configuration
    
    Args:
        df: DataFrame with OHLCV data
        feature_config: Dictionary specifying which features to generate and their parameters
                       If None, uses default configuration
    
    Returns:
        DataFrame with generated features
    """
    if feature_config is None:
        feature_config = {
            'returns': {'periods': [1, 5, 10]},
            'sma': {'periods': [10, 30, 50]},
            'volatility': {'periods': [10, 30]},
            'rsi': {'periods': [14, 28]},
            'volume': {'periods': [5, 10, 20]}
        }
    
    df = df.copy()
    generator = FeatureGenerator()
    
    # Generate features based on config
    for feature_type, params in feature_config.items():
        if feature_type == 'returns':
            df = generator.returns(df, params.get('periods', [1, 5, 10]))
        elif feature_type == 'sma':
            df = generator.sma(df, params.get('periods', [10, 30, 50]))
        elif feature_type == 'volatility':
            df = generator.volatility(df, params.get('periods', [10, 30]))
        elif feature_type == 'rsi':
            df = generator.rsi(df, params.get('periods', [14, 28]))
        elif feature_type == 'volume':
            df = generator.volume_features(df, params.get('periods', [5, 10, 20]))
    
    df.dropna(inplace=True)
    return df

def list_available_features(feature_config: Dict[str, Any] = None) -> List[str]:
    """List all available features based on the configuration"""
    if feature_config is None:
        feature_config = {
            'returns': {'periods': [1, 5, 10]},
            'sma': {'periods': [10, 30, 50]},
            'volatility': {'periods': [10, 30]},
            'rsi': {'periods': [14, 28]},
            'volume': {'periods': [5, 10, 20]}
        }
    
    features = []
    
    # Returns
    for period in feature_config.get('returns', {}).get('periods', []):
        features.append(f'return_{period}')
    
    # SMAs and ratios
    sma_periods = feature_config.get('sma', {}).get('periods', [])
    for period in sma_periods:
        features.append(f'sma_{period}')
    for i in range(len(sma_periods)-1):
        features.append(f'sma_ratio_{sma_periods[i]}_{sma_periods[i+1]}')
    
    # Volatility
    for period in feature_config.get('volatility', {}).get('periods', []):
        features.append(f'volatility_{period}')
    
    # RSI
    for period in feature_config.get('rsi', {}).get('periods', []):
        features.append(f'rsi_{period}')
    
    # Volume
    for period in feature_config.get('volume', {}).get('periods', []):
        features.append(f'volume_sma_{period}')
        features.append(f'volume_ratio_{period}')
    
    return features