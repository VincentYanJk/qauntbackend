"""
Technical Analysis based trading strategy
"""
import backtrader as bt
from ..indicators import (
    RSI, MACD, BollingerBands, Stochastic, WilliamsR
)

class Technical_Voting3_Strategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('bb_period', 20),
        ('bb_devfactor', 2),
        ('stoch_period', 14),
        ('stoch_dfast', 3),
        ('stoch_dslow', 3),
        ('williams_period', 14),
    )
    
    def __init__(self):
        # Initialize indicators
        self.rsi = RSI(period=self.p.rsi_period)
        self.macd = MACD(
            fast=self.p.macd_fast,
            slow=self.p.macd_slow,
            signal_period=self.p.macd_signal
        )
        self.bollinger = BollingerBands(
            period=self.p.bb_period,
            devfactor=self.p.bb_devfactor
        )
        self.stochastic = Stochastic(
            period=self.p.stoch_period,
            period_dfast=self.p.stoch_dfast,
            period_dslow=self.p.stoch_dslow
        )
        self.williams = WilliamsR(period=self.p.williams_period)
        
        # For position management
        self.order = None
        self.last_signal = None
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED - Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            else:
                self.log(f'SELL EXECUTED - Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                
        self.order = None
        
    def log(self, txt):
        dt = self.datas[0].datetime.datetime(0)
        print(f'{dt} - {txt}')
        
    def next(self):
        if self.order:
            return
            
        # Calculate signals
        rsi_signal = (
            1 if self.rsi.rsi[0] < self.p.rsi_oversold else
            -1 if self.rsi.rsi[0] > self.p.rsi_overbought else
            0
        )
        
        macd_signal = (
            1 if self.macd.macd[0] > self.macd.signal[0] and self.macd.hist[0] > 0 else
            -1 if self.macd.macd[0] < self.macd.signal[0] and self.macd.hist[0] < 0 else
            0
        )
        
        bb_signal = (
            1 if self.data.close[0] < self.bollinger.bot[0] else
            -1 if self.data.close[0] > self.bollinger.top[0] else
            0
        )
        
        stoch_signal = (
            1 if self.stochastic.percK[0] < 20 and self.stochastic.percD[0] < 20 else
            -1 if self.stochastic.percK[0] > 80 and self.stochastic.percD[0] > 80 else
            0
        )
        
        williams_signal = (
            1 if self.williams.williamsr[0] < -80 else
            -1 if self.williams.williamsr[0] > -20 else
            0
        )
        
        # Combine signals (simple majority voting)
        signals = [rsi_signal, macd_signal, bb_signal, stoch_signal, williams_signal]
        buy_votes = len([s for s in signals if s == 1])
        sell_votes = len([s for s in signals if s == -1])
        
        final_signal = (
            1 if buy_votes > sell_votes and buy_votes >= 3 else
            -1 if sell_votes > buy_votes and sell_votes >= 3 else
            0
        )
        
        # Execute trades
        if not self.position:  # not in the market
            if final_signal == 1:  # buy signal
                self.log(f'BUY CREATE - RSI: {self.rsi.rsi[0]:.2f}, MACD Hist: {self.macd.hist[0]:.2f}')
                self.order = self.buy()
            elif final_signal == -1:  # sell signal
                self.log(f'SELL CREATE - RSI: {self.rsi.rsi[0]:.2f}, MACD Hist: {self.macd.hist[0]:.2f}')
                self.order = self.sell()
        
        else:  # in the market
            if (self.position.size > 0 and final_signal == -1) or \
               (self.position.size < 0 and final_signal == 1):
                self.log('CLOSE CREATE')
                self.order = self.close()
                
        self.last_signal = final_signal 