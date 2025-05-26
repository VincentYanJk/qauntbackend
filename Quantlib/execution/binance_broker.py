from binance.client import Client
from abc import ABC, abstractmethod

class BrokerInterface(ABC):
    @abstractmethod
    def buy(self, symbol, quantity, price=None, is_futures=False): pass

    @abstractmethod
    def sell(self, symbol, quantity, price=None, is_futures=False): pass

    @abstractmethod
    def get_balance(self, asset="USDT", is_futures=False): pass

    @abstractmethod
    def get_position(self, symbol): pass

    @abstractmethod
    def get_account_info(self, is_futures=False): pass

    @abstractmethod
    def set_leverage(self, symbol, leverage): pass


class BinanceBroker(BrokerInterface):
    def __init__(self, api_key, api_secret, use_futures=False, testnet=False):
        self.use_futures = use_futures
        self.client = Client(api_key, api_secret)

        if testnet:
            self.client.API_URL = 'https://testnet.binance.vision/api'
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
        if use_futures:
            self.client.API_URL = 'https://fapi.binance.com/fapi'

    def buy(self, symbol, quantity, price=None, is_futures=None):
        is_futures = is_futures if is_futures is not None else self.use_futures
        order_type = "MARKET" if price is None else "LIMIT"
        if is_futures:
            return self.client.futures_create_order(
                symbol=symbol, side="BUY", type=order_type, quantity=quantity, price=price
            )
        else:
            return self.client.create_order(
                symbol=symbol, side="BUY", type=order_type, quantity=quantity, price=price
            )

    def sell(self, symbol, quantity, price=None, is_futures=None):
        is_futures = is_futures if is_futures is not None else self.use_futures
        order_type = "MARKET" if price is None else "LIMIT"
        if is_futures:
            return self.client.futures_create_order(
                symbol=symbol, side="SELL", type=order_type, quantity=quantity, price=price
            )
        else:
            return self.client.create_order(
                symbol=symbol, side="SELL", type=order_type, quantity=quantity, price=price
            )

    def get_balance(self, asset="USDT", is_futures=None):
        is_futures = is_futures if is_futures is not None else self.use_futures
        if is_futures:
            balances = self.client.futures_account_balance()
            for b in balances:
                if b["asset"] == asset:
                    return b["balance"]
            return None
        else:
            return self.client.get_asset_balance(asset=asset)

    def get_position(self, symbol):
        positions = self.client.futures_position_information(symbol=symbol)
        for pos in positions:
            if float(pos["positionAmt"]) != 0:
                return pos
        return None

    def get_account_info(self, is_futures=None):
        is_futures = is_futures if is_futures is not None else self.use_futures
        return self.client.futures_account() if is_futures else self.client.get_account()

    def set_leverage(self, symbol, leverage):
        return self.client.futures_change_leverage(symbol=symbol, leverage=leverage)

    def get_available_symbols(self, is_futures=False):
        if is_futures or self.use_futures:
            exchange_info = self.client.futures_exchange_info()
            return [s["symbol"] for s in exchange_info["symbols"] if s["contractType"] == "PERPETUAL"]
        else:
            exchange_info = self.client.get_exchange_info()
            return [s["symbol"] for s in exchange_info["symbols"] if s["status"] == "TRADING"]
    