"""
Machine Learning based trading strategy
"""
import backtrader as bt
import numpy as np
import pandas as pd

class MLSignalStrategy(bt.Strategy):
    params = (
        ('model', None),  # ML model instance
        ('features', ['return_1', 'sma_ratio', 'volatility']),  # Features to use for prediction
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
        if len(self) < 2:  # Need at least 2 data points
            return
            
        # Don't trade if we have a pending order
        if self.order:
            return

        # Get the current market data
        data = self._prepare_data()
        
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
        # Basic feature preparation
        data = {}
        
        # Calculate return
        close = self.data_close[0]
        close_prev = self.data_close[-1]
        data['return_1'] = (close - close_prev) / close_prev
            
        # Calculate SMA ratio
        sma_10 = np.mean([self.data_close[-i] for i in range(10)])
        sma_30 = np.mean([self.data_close[-i] for i in range(30)])
        data['sma_ratio'] = sma_10 / sma_30
            
        # Calculate volatility
        prices = [self.data_close[-i] for i in range(10)]
        data['volatility'] = np.std(prices)
            
        # Convert to DataFrame with a single row
        df = pd.DataFrame([data])
        print(f"Features for prediction: {df.to_dict('records')[0]}")
        return df
        
    def _execute_trades(self, signal):
        # More aggressive trading logic
        if signal > 0:  # Buy signal
            if not self.position:  # If we don't have a position, buy
                print(f"⬆️ BUYING at {self.data_close[0]:.2f}")
                self.order = self.buy()
            # If we have a short position, close it and go long
            elif self.position.size < 0:
                print(f"🔄 CLOSING SHORT & GOING LONG at {self.data_close[0]:.2f}")
                self.order = self.close()
                self.order = self.buy()
        else:  # Sell signal
            if not self.position:  # If we don't have a position, go short
                print(f"⬇️ SELLING at {self.data_close[0]:.2f}")
                self.order = self.sell()
            # If we have a long position, close it and go short
            elif self.position.size > 0:
                print(f"🔄 CLOSING LONG & GOING SHORT at {self.data_close[0]:.2f}")
                self.order = self.close()
                self.order = self.sell()
            
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'BUY EXECUTED at {order.executed.price:.2f}')
            elif order.issell():
                print(f'SELL EXECUTED at {order.executed.price:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print('Order Failed')
        self.order = None  # Reset order