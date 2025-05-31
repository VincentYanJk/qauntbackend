import pandas as pd
import numpy as np
import backtrader as bt
from typing import List, Callable

class DataProcessor:
    def __init__(self):
        self.indicators = {}  # Dictionary of name: calculation_function
        
    def add_indicator(self, name: str, calculation_func: Callable):
        """Add a new indicator calculation function"""
        self.indicators[name] = calculation_func
        
    def remove_indicator(self, name: str):
        """Remove an indicator by name"""
        self.indicators.pop(name, None)
        
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process data with registered indicators"""
        processed = df.copy()
        
        for name, func in self.indicators.items():
            try:
                result = func(processed)
                if isinstance(result, (pd.Series, np.ndarray)):
                    processed[name] = result
                elif isinstance(result, pd.DataFrame):
                    # Prefix columns with indicator name to avoid conflicts
                    result = result.add_prefix(f"{name}_")
                    processed = pd.concat([processed, result], axis=1)
            except Exception as e:
                print(f"Error calculating indicator {name}: {e}")
                
        return processed

def preprocess_btc_csv(csv_path: str) -> pd.DataFrame:
    """Load and preprocess BTC price data from CSV"""
    df = pd.read_csv(csv_path)
    df['datetime'] = pd.to_datetime(df['timestamp'])
    df.set_index('datetime', inplace=True)
    return df

# Example indicator functions
def calculate_sma(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Calculate Simple Moving Average"""
    return df['close'].rolling(window=window).mean()

def calculate_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))