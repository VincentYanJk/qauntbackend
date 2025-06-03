"""
Buy and Hold Strategy
This strategy buys at the first opportunity and holds until the end
"""
from .base_strategy import BaseStrategy
import backtrader as bt

class BuyAndHoldStrategy(BaseStrategy):
    """
    Simple Buy and Hold Strategy
    Buys on the first bar and holds until the end
    Used as a benchmark for comparing other strategies
    """
    
    params = (
        ('trade_size', 1.0),  # Default to using 100% of available capital
    )

    def __init__(self):
        super(BuyAndHoldStrategy, self).__init__()
        self.order = None  # Track pending orders
        self.bought = False  # Track if we've already bought
        
    def setup_indicators(self):
        # No indicators needed for buy and hold
        pass
        
    def next(self):
        # Only buy if we haven't bought yet and don't have a pending order
        if not self.bought and not self.order and not self.position:
            self.log(f'PLACING BUY ORDER - Cash: ${self.broker.getcash():.2f}, Close: ${self.data.close[0]:.2f}')
            self.order = self.execute_buy()
            
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.bought = True
                self.log(f'BUY EXECUTED - Price: ${order.executed.price:.2f}, Size: {order.executed.size:.6f}, Cost: ${order.executed.value:.2f}, Comm: ${order.executed.comm:.2f}')
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Failed')
            self.bought = False
            
        self.order = None
            
    def stop(self):
        """Called when backtest ends"""
        # Calculate and log the final portfolio value
        portfolio_value = self.broker.getcash()
        if self.position:
            portfolio_value += self.position.size * self.data.close[0]
        self.log(f'Buy and Hold Final Portfolio Value: ${portfolio_value:.2f}') 