
from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    save_trade_log
)


from Quantlib.strategies.ml_signal_strategy import MLSignalStrategy
from Quantlib.backtest.engine import run_backtest

run_backtest(
    strategy_class=lambda: MLSignalStrategy(use_ml=True, model_type="xgboost"),
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=True
)

# Visualization and trade logging
plot_equity_curve(df["equity"])
plot_drawdown(df["equity"])
plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
save_trade_log(trades)
