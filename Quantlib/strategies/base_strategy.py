"""
Base strategy class that all strategies should inherit from
"""
import backtrader as bt

class BaseStrategy(bt.Strategy):
    """Base class for all trading strategies"""
    
    params = (
        ('trade_size', 1.0),  # Default position size
    )

    def __init__(self):
        """Initialize strategy and register indicators"""
        self.order = None
        self.setup_indicators()

    def setup_indicators(self):
        """Setup technical indicators - override in child classes"""
        pass

    def next(self):
        """Main strategy logic - must be implemented by child classes"""
        raise NotImplementedError("Strategies must implement next() method")

    def execute_buy(self):
        """Execute buy order with position sizing"""
        if not self.position:
            self.buy(size=self.params.trade_size)

    def execute_sell(self):
        """Execute sell order with position sizing"""
        if self.position:
            self.sell(size=self.params.trade_size)

    def notify_order(self, order):
        """Handle order status updates"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def log(self, txt, dt=None):
        """Logging function"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')