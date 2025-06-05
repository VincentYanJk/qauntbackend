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
            cash = self.broker.getcash()  # Get available cash
            price = self.data.close[0]  # Current price
            trade_cash = cash * self.params.trade_size  # Calculate cash to use for trade
            
            # Get commission and slippage info
            comminfo = self.broker.getcommissioninfo(self.data0)
            commission_rate = comminfo.p.commission
            slippage = self.broker.p.slip_perc if hasattr(self.broker.p, 'slip_perc') else 0
            
            # Calculate total cost rate (commission + slippage)
            total_cost_rate = commission_rate + slippage
            
            # Calculate position size accounting for both commission and slippage
            # For a total cost rate r:
            # size * price * (1 + r) = trade_cash
            # size = trade_cash / (price * (1 + r))
            size = trade_cash / (price * (1 + total_cost_rate))
            
            self.buy(size=size)

    def execute_sell(self):
        """Execute sell order with position sizing"""
        if self.position:
            # Sell entire position
            self.sell(size=self.position.size)

    def notify_order(self, order):
        """Handle order status updates"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            # Calculate portfolio value using current close price
            cash = self.broker.getcash()
            position_value = 0
            if order.isbuy():
                # For buy orders, use the new position size
                position_value = order.executed.size * self.data.close[0]
               # self.log(f' calculation current day close price: {self.data.close[0]:.2f} | open price: {self.data.open[0]:.2f}')
                 
            else:
                # For sell orders, position is already closed
                position_value = 0
            portfolio_value = cash + position_value
            
            if order.isbuy():
                self.log(f'BUY EXECUTED at {order.executed.price:.2f} | Size: {order.executed.size:.6f} | Commission: ${order.executed.comm:.2f} | Portfolio Value: ${portfolio_value:.2f}')
            else:
                self.log(f'SELL EXECUTED at {order.executed.price:.2f} | Size: {order.executed.size:.6f} | Commission: ${order.executed.comm:.2f} | Portfolio Value: ${portfolio_value:.2f}')
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def log(self, txt, dt=None):
        """Logging function"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')