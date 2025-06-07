"""
Bollinger Bands strategy implementation
"""
from .base_strategy import BaseStrategy
from Quantlib.indicators.bollinger import BollingerBands

class BollingerBand(BaseStrategy):
    params = (
        ('period', 20),  # Bollinger Bands period
        ('devfactor', 2.0),  # Number of standard deviations
        ('trade_size', 1.0),  # Position size
    )

    def setup_indicators(self):
        # Initialize Bollinger Bands indicator
        self.bollinger = BollingerBands(
            self.data.close,
            period=self.params.period,
            devfactor=self.params.devfactor
        )
        
    def next(self):
        # Buy when price crosses below lower band
        if not self.position and self.data.close[0] < self.bollinger.bot[0]:
            self.execute_buy()
            
        # Sell when price crosses above upper band
        elif self.position and self.data.close[0] > self.bollinger.top[0]:
            self.execute_sell() 