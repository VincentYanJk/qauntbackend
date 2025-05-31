from Quantlib.forecast.trainer.trainer import train_model
from Quantlib.backtest.engine import run_backtest
from Quantlib.visualization.visualize import plot_equity_curve
from Quantlib.strategies.ml_signal_strategy import MLSignalStrategy

train_model(
    df_path="data/BTCUSDT.csv",
    model_type="xgboost",
    save_path="models/xgb_model.pkl"
)

equity = run_backtest(
    strategy_class=lambda: MLSignalStrategy(use_ml=True, model_type="xgboost", trade_size=0.1),
    data_path="data/BTCUSDT.csv",
    cash=100000,
    plot=False
)

plot_equity_curve(equity)