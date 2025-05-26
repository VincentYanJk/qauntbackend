from Quantlib.forecast.features import generate_features
from Quantlib.forecast.factory import load_model
from Quantlib.backtest.engine import run_backtest
from Quantlib.strategies.ml_signal_strategy import MLSignalStrategy
import pandas as pd
import joblib
import os


class FactorPipeline:
    def __init__(self, df_path, feature_set, model_type="xgboost", model_save_path="models/auto_model.pkl"):
        self.df_path = df_path
        self.feature_set = feature_set
        self.model_type = model_type
        self.model_save_path = model_save_path

    def train(self):
        df = pd.read_csv(self.df_path, parse_dates=["datetime"])
        df = generate_features(df)
        df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

        X = df[self.feature_set]
        y = df["target"]

        from xgboost import XGBClassifier
        model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
        model.fit(X, y)

        os.makedirs(os.path.dirname(self.model_save_path), exist_ok=True)
        joblib.dump(model, self.model_save_path)
        print(f"Model trained and saved to {self.model_save_path}")

    def backtest(self):
        class CustomMLStrategy(MLSignalStrategy):
            def __init__(self):
                super().__init__(use_ml=True, model_type=None)
                from Quantlib.forecast.predictor.tree_predictor import TreePredictor
                self.model = TreePredictor(self.model_save_path)
                self.feature_set = self.params.feature_set

            def next(self):
                if not self.model or len(self) < 30:
                    return
                row = {f: self._get_feature(f) for f in self.feature_set}
                signal = self.model.predict(row)
                if not self.position and signal == 1:
                    self.buy()
                elif self.position and signal == 0:
                    self.sell()

            def _get_feature(self, name):
                if name == "return_1":
                    return (self.data.close[-1] - self.data.close[-2]) / self.data.close[-2]
                elif name == "sma_ratio":
                    return sum(self.data.close.get(size=10)) / sum(self.data.close.get(size=30))
                elif name == "volatility":
                    return self.data.close.get(size=10).std()
                else:
                    raise ValueError(f"Unknown feature: {name}")

        from Quantlib.visualization.visualize import plot_equity_curve

        df, trades = run_backtest(
            strategy_class=lambda: CustomMLStrategy(),
            data_path=self.df_path,
            cash=100000,
            plot=False
        )

        plot_equity_curve(df["equity"])
