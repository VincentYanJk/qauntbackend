from Quantlib.forecast.pipeline import FactorPipeline
from Quantlib.visualization.visualize import plot_equity_curve

pipeline = FactorPipeline(
    df_path="data/BTCUSDT.csv",
    feature_set=["sma_ratio", "volatility"],
    model_type="xgboost",
    model_save_path="models/xgb_auto.pkl"
)

pipeline.train()
equity = pipeline.backtest()
plot_equity_curve(equity)