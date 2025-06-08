"""
RSI + Bollinger Bands combined strategy implementation
"""
from .base_strategy import BaseStrategy
from Quantlib.indicators.rsi import RSI
from Quantlib.indicators.bollinger import BollingerBands

class RSIBollingerStrategy(BaseStrategy):
    params = (
        ('rsi_period', 20),  # RSI period
        ('rsi_oversold', 20),  # RSI oversold threshold
        ('rsi_overbought', 60),  # RSI overbought threshold
        ('bb_period', 10),  # Bollinger Bands period
        ('bb_devfactor', 2.5),  # Number of standard deviations
        ('trade_size', 1.0),  # Position size
    )

    def setup_indicators(self):
        # Initialize RSI indicator
        self.rsi = RSI(
            self.data.close,
            period=self.params.rsi_period
        )
        
        # Initialize Bollinger Bands indicator
        self.bollinger = BollingerBands(
            self.data.close,
            period=self.params.bb_period,
            devfactor=self.params.bb_devfactor
        )
        
    def next(self):
        # Buy when price is below lower band AND RSI is oversold
        if not self.position and \
           self.data.close[0] < self.bollinger.bot[0] and \
           self.rsi[0] < self.params.rsi_oversold:
            self.execute_buy()
            
        # Sell when price is above upper band AND RSI is overbought
        elif self.position and \
             self.data.close[0] > self.bollinger.top[0] and \
             self.rsi[0] > self.params.rsi_overbought:
            self.execute_sell() 