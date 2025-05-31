from Quantlib.forecast.trainer.deep_trainer import train_lstm_model
from Quantlib.backtest.engine import run_backtest
from Quantlib.visualization.visualize import plot_equity_curve
from Quantlib.strategies.ml_signal_strategy import MLSignalStrategy

train_lstm_model(
    csv_path="data/BTCUSDT.csv",
    save_path="models/lstm_model.pt",
    seq_len=10,
    epochs=5
)

equity = run_backtest(
    strategy_class=lambda: MLSignalStrategy(use_ml=True, model_type="lstm", trade_size=0.1),
    data_path="data/BTCUSDT.csv",
    cash=100000,
    plot=False
)

plot_equity_curve(equity)