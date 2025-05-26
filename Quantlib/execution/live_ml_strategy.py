from Quantlib.execution.trade_executor import TradeExecutor
from Quantlib.execution.symbol_config import round_quantity

class LiveMLStrategy:
    def __init__(self, executor: TradeExecutor, model, symbol="BTCUSDT", qty=0.001, features=["sma_ratio", "volatility"]):
        self.executor = executor
        self.model = model
        self.symbol = symbol
        self.qty = qty
        self.features = features

    def on_new_tick(self, data_row):
        x = {f: data_row[f] for f in self.features}
        signal = self.model.predict(x)
        quantity = round_quantity(self.symbol, self.qty)

        if signal == 1:
            self.executor.buy(self.symbol, quantity)
        elif signal == 0:
            self.executor.sell(self.symbol, quantity)