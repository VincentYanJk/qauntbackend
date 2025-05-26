import pandas as pd

def generate_features(df):
    df = df.copy()
    df['return_1'] = df['close'].pct_change()
    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_30'] = df['close'].rolling(window=30).mean()
    df['sma_ratio'] = df['sma_10'] / df['sma_30']
    df['volatility'] = df['return_1'].rolling(window=10).std()
    df.dropna(inplace=True)
    return df