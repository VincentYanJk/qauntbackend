"""
Machine Learning based trading strategy
"""
import backtrader as bt
import numpy as np
import pandas as pd
from typing import Dict, Any, List

def generate_features_for_backtest(df: pd.DataFrame, feature_config: Dict[str, Any] = None) -> pd.DataFrame:
    """Simplified feature generator for backtesting"""
    if feature_config is None:
        feature_config = {
            'returns': {'periods': [1, 5, 10]},
            'sma': {'periods': [10, 30, 50]},
            'volatility': {'periods': [10, 30]},
            'rsi': {'periods': [14, 28]},
            'volume': {'periods': [5, 10, 20]},
            'momentum': {'periods': [5]}
        }
    
    df = df.copy()
    
    # Returns
    for period in feature_config.get('returns', {}).get('periods', []):
        df[f'return_{period}'] = df['close'].pct_change(period)
    
    # SMAs and ratios
    sma_periods = feature_config.get('sma', {}).get('periods', [])
    for period in sma_periods:
        df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
    for i in range(len(sma_periods)-1):
        short_period = sma_periods[i]
        long_period = sma_periods[i+1]
        df[f'sma_ratio_{short_period}_{long_period}'] = (
            df[f'sma_{short_period}'] / df[f'sma_{long_period}']
        )
    
    # Volatility
    for period in feature_config.get('volatility', {}).get('periods', []):
        df[f'volatility_{period}'] = df['return_1'].rolling(window=period).std()
    
    # RSI
    for period in feature_config.get('rsi', {}).get('periods', []):
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
    
    # Volume
    volume_col = 'Volume' if 'Volume' in df.columns else 'volume'
    if volume_col in df.columns:
        for period in feature_config.get('volume', {}).get('periods', []):
            df[f'volume_sma_{period}'] = df[volume_col].rolling(window=period).mean()
            df[f'volume_ratio_{period}'] = df[volume_col] / df[f'volume_sma_{period}']
    
    # Momentum
    for period in feature_config.get('momentum', {}).get('periods', []):
        df[f'momentum_{period}'] = df['close'] - df['close'].shift(period)
    
    return df

class MLSignalStrategy(bt.Strategy):
    params = (
        ('model', None),  # ML model instance
        ('features', ['return_1', 'sma_ratio', 'volatility']),  # Features to use for prediction
        ('feature_config', None),  # Feature generation configuration
        ('lookback', 50),  # Number of bars to look back for feature calculation
        ('trade_size', 1.0),  # Position size as fraction of portfolio
    )

    def __init__(self):
        super().__init__()
        if self.params.model is None:
            raise ValueError("Model must be provided")
        self.model = self.params.model
        self.data_close = self.datas[0].close
        self.data_volume = self.datas[0].volume
        self.order = None
        self.last_signal = None
        print("Strategy initialized with features:", self.params.features)

    def next(self):
        if len(self) < self.params.lookback:  # Need enough data for feature calculation
            return
            
        # Don't trade if we have a pending order
        if self.order:
            return

        # Get the current market data
        data = self._prepare_data()
        if data is None:
            return
        
        # Get prediction from model
        try:
            signal = self.model.predict(data)[0]  # Get the first prediction
            print(f"Date: {self.datas[0].datetime.date(0)}, Close: {self.data_close[0]:.2f}, Signal: {signal}")
            
            # Only trade if signal changes
            if signal != self.last_signal:
                self._execute_trades(signal)
                self.last_signal = signal
                
        except Exception as e:
            print(f"Prediction error: {e}")
        
    def _prepare_data(self):
        try:
            # Prepare historical data for feature calculation
            hist_data = {
                'datetime': pd.Series([self.datas[0].datetime.datetime(-i) for i in range(self.params.lookback-1, -1, -1)]),
                'open': pd.Series([self.datas[0].open[-i] for i in range(self.params.lookback-1, -1, -1)]),
                'high': pd.Series([self.datas[0].high[-i] for i in range(self.params.lookback-1, -1, -1)]),
                'low': pd.Series([self.datas[0].low[-i] for i in range(self.params.lookback-1, -1, -1)]),
                'close': pd.Series([self.datas[0].close[-i] for i in range(self.params.lookback-1, -1, -1)]),
                'Volume': pd.Series([self.datas[0].volume[-i] for i in range(self.params.lookback-1, -1, -1)])
            }
            df = pd.DataFrame(hist_data)
            
            # Generate features using our feature generator
            df = generate_features_for_backtest(df, self.params.feature_config)
            
            # Get the last row (current bar) and select only the required features
            current_features = df.iloc[-1:][self.params.features]
            print(f"Features for prediction: {current_features.to_dict('records')[0]}")
            return current_features
            
        except Exception as e:
            print(f"Error preparing data: {e}")
            return None
        
    def _execute_trades(self, signal):
        # Calculate position size
        cash = self.broker.getcash()
        price = self.data_close[0]
        trade_cash = cash * self.params.trade_size
        
        # Get commission info
        comminfo = self.broker.getcommissioninfo(self.data0)
        commission_rate = comminfo.p.commission
        slippage = self.broker.p.slip_perc if hasattr(self.broker.p, 'slip_perc') else 0
        
        # Calculate total cost rate
        total_cost_rate = commission_rate + slippage
        
        # Calculate size accounting for costs
        size = trade_cash / (price * (1 + total_cost_rate))

        # More aggressive trading logic
        if signal > 0:  # Buy signal
            if not self.position:  # If we don't have a position, buy
                print(f"⬆️ BUYING at {self.data_close[0]:.2f}")
                self.order = self.buy(size=size)
            # If we have a short position, close it and go long
            elif self.position.size < 0:
                print(f"🔄 CLOSING SHORT & GOING LONG at {self.data_close[0]:.2f}")
                self.order = self.close()
                self.order = self.buy(size=size)
        else:  # Sell signal
            if not self.position:  # If we don't have a position, go short
                print(f"⬇️ SELLING at {self.data_close[0]:.2f}")
                self.order = self.sell(size=size)
            # If we have a long position, close it and go short
            elif self.position.size > 0:
                print(f"🔄 CLOSING LONG & GOING SHORT at {self.data_close[0]:.2f}")
                self.order = self.close()
                self.order = self.sell(size=size)
            
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'BUY EXECUTED at {order.executed.price:.2f}')
            elif order.issell():
                print(f'SELL EXECUTED at {order.executed.price:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print('Order Failed')
        self.order = None  # Reset order