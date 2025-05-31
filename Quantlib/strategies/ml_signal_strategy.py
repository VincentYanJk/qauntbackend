import backtrader as bt

class MLSignalStrategy(bt.Strategy):
    params = dict(
        use_ml=True,
        model_type="xgboost",
        trade_size=1.0
    )

    def __init__(self):
        self.model = None
        if self.params.use_ml:
            from Quantlib.forecast.factory import load_model
            self.model = load_model(self.params.model_type)

    def next(self):
        if not self.model or len(self) < 30:
            return

        row = {
            'return_1': (self.data.close[-1] - self.data.close[-2]) / self.data.close[-2],
            'sma_ratio': sum(self.data.close.get(size=10)) / sum(self.data.close.get(size=30)),
            'volatility': self.data.close.get(size=10).std()
        }

        signal = self.model.predict(row)
        if not self.position and signal == 1:
            self.buy(size=self.params.trade_size)
        elif self.position and signal == 0:
            self.sell(size=self.params.trade_size)