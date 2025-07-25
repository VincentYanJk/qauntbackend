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
        # First calculate returns if not already present
        if 'return_1' not in df.columns:
            df['return_1'] = df['close'].pct_change()
            
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
        for period in periods:
            df[f'volume_sma_{period}'] = df['volume'].rolling(window=period).mean()
            df[f'volume_ratio_{period}'] = df['volume'] / df[f'volume_sma_{period}']
        return df

    @staticmethod
    def mfi(df: pd.DataFrame, periods: List[int] = [14], overbought: float = 80.0, oversold: float = 20.0) -> pd.DataFrame:
        """Calculate Money Flow Index and signals for multiple periods
        
        Args:
            df: DataFrame with OHLCV data
            periods: List of periods to calculate MFI for
            overbought: Threshold above which asset is considered overbought (default: 80)
            oversold: Threshold below which asset is considered oversold (default: 20)
            
        Returns:
            DataFrame with MFI values and signals added
        """
        df = df.copy()
        
        for period in periods:
            # Calculate typical price
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            
            # Get the raw money flow
            raw_money_flow = typical_price * df['volume']
            
            # Get the money flow direction
            price_change = typical_price.diff()
            positive_flow = raw_money_flow.where(price_change > 0, 0)
            negative_flow = raw_money_flow.where(price_change < 0, 0)
            
            # Calculate the money flow ratio
            positive_flow_sum = positive_flow.rolling(window=period).sum()
            negative_flow_sum = negative_flow.rolling(window=period).sum()
            money_flow_ratio = positive_flow_sum / negative_flow_sum
            
            # Calculate MFI
            mfi = 100 - (100 / (1 + money_flow_ratio))
            df[f'mfi_{period}'] = mfi
            
            # Generate overbought/oversold signals
            df[f'mfi_{period}_overbought'] = (mfi > overbought).astype(int)
            df[f'mfi_{period}_oversold'] = (mfi < oversold).astype(int)
            
            # Generate signal changes (1 for entering signal, -1 for exiting signal)
            df[f'mfi_{period}_overbought_change'] = df[f'mfi_{period}_overbought'].diff()
            df[f'mfi_{period}_oversold_change'] = df[f'mfi_{period}_oversold'].diff()
            
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
            'volume': {'periods': [5, 10, 20]},
            'mfi': {
                'periods': [14],
                'overbought': 80.0,
                'oversold': 20.0
            }
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
        elif feature_type == 'mfi':
            df = generator.mfi(
                df, 
                params.get('periods', [14]),
                params.get('overbought', 80.0),
                params.get('oversold', 20.0)
            )
    
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
            'volume': {'periods': [5, 10, 20]},
            'mfi': {
                'periods': [14],
                'overbought': 80.0,
                'oversold': 20.0
            }
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
    
    # MFI
    for period in feature_config.get('mfi', {}).get('periods', []):
        features.append(f'mfi_{period}')
        features.append(f'mfi_{period}_overbought')
        features.append(f'mfi_{period}_oversold')
        features.append(f'mfi_{period}_overbought_change')
        features.append(f'mfi_{period}_oversold_change')
    
    return features