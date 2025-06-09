import sys
print(f"Using Python from: {sys.executable}")

from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    save_trade_log
)

from Quantlib.strategies.multi_filter_strategy import MultiFilterStrategy
from Quantlib.backtest.engine import run_backtest

# Define commission and slippage settings
commission_scheme = {
    'commission': 0.002,  # 0.2% trading fee (typical for crypto exchanges)
    'margin': None,      # No margin trading
    'mult': 1.0,         # No leverage
}

# Define slippage settings
slippage_scheme = {
    'slip_perc': 0.001,  # 0.1% slippage (conservative estimate)
    'slip_fixed': 0.0,   # No fixed slippage
    'slip_open': True,   # Apply slippage on open orders
}

# Strategy parameters
strategy_params = {
    'momentum_period': 5,     # 5-day momentum
    'sma_period': 20,         # 20-day SMA for trend
    'volume_period': 10,      # 10-day volume MA
    'atr_period': 14,         # 14-day ATR
    'atr_threshold': 0.05,    # 5% ATR threshold
    'rsi_period': 14,         # 14-day RSI
    'rsi_threshold': 70,      # RSI overbought level
    'trade_size': 0.5,        # Use 50% of portfolio per trade
}

# Run backtest
df, trades_df, performance = run_backtest(
    strategy_class=MultiFilterStrategy,
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=True,
    kwargs={
        **strategy_params,
        'commission_scheme': commission_scheme,
        'slippage_scheme': slippage_scheme
    }
)

# Print all performance metrics
print("\nStrategy Parameters:")
for param, value in strategy_params.items():
    print(f"{param}: {value}")

print("\nPerformance Metrics:")
performance.print_all()

# Visualization and trade logging
plot_equity_curve(df["equity"])
plot_drawdown(df["equity"])
plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
save_trade_log(trades_df)

# Print summary of conditions that prevented trades (from strategy logs)
print("\nDetailed trade analysis can be found in the generated trade log.") 