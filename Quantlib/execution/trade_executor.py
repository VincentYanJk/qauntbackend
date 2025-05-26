from abc import ABC, abstractmethod

class TradeExecutor(ABC):
    @abstractmethod
    def buy(self, symbol, quantity): pass

    @abstractmethod
    def sell(self, symbol, quantity): pass

    @abstractmethod
    def get_position(self, symbol): pass

    @abstractmethod
    def get_balance(self, asset="USDT"): pass


class BacktestExecutor(TradeExecutor):
    def __init__(self, strategy):
        self.strategy = strategy

    def buy(self, symbol, quantity):
        self.strategy.buy(size=quantity)

    def sell(self, symbol, quantity):
        self.strategy.sell(size=quantity)

    def get_position(self, symbol):
        return self.strategy.position.size

    def get_balance(self, asset="USDT"):
        return self.strategy.broker.getvalue()


class LiveExecutor(TradeExecutor):
    def __init__(self, broker, default_symbol):
        self.broker = broker
        self.symbol = default_symbol

    def buy(self, symbol, quantity):
        return self.broker.buy(symbol=symbol, quantity=quantity)

    def sell(self, symbol, quantity):
        return self.broker.sell(symbol=symbol, quantity=quantity)

    def get_position(self, symbol):
        return self.broker.get_position(symbol)

    def get_balance(self, asset="USDT"):
        return self.broker.get_balance(asset=asset)