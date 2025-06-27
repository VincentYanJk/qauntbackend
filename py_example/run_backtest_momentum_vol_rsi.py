import sys
print(f"Using Python from: {sys.executable}")

from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    plot_trade_returns,
    save_trade_log
)

from Quantlib.strategies.momentum_vol_rsi import MomentumVolRSI
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
    'momentum_period': 10,        # 10-day momentum
    'vol_period': 20,            # 20-day volume MA
    'rsi_period': 14,            # 14-day RSI
    'trade_size': 0.5,           # Use 50% of portfolio per trade
}

# Run backtest
df, trades_df, performance = run_backtest(
    strategy_class=MomentumVolRSI,
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=True,
    kwargs={
        **strategy_params,
        'commission_scheme': commission_scheme,
        'slippage_scheme': slippage_scheme
    }
)

# Print strategy parameters
print("\nStrategy Parameters:")
for param, value in strategy_params.items():
    print(f"{param}: {value}")

print("\nPerformance Metrics:")
performance.print_all()

# Visualization and trade logging
plot_equity_curve(df["equity"])
plot_drawdown(df["equity"])
plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
plot_trade_returns(trades_df)
save_trade_log(trades_df)

# Print summary
print("\nStrategy Logic:")
print("Buy Signal Conditions:")
print("1. 10-day momentum > 0")
print("2. 20-day/10-day volume ratio > 1")
print("3. RSI < 30 (oversold)")
print("\nSell Signal Conditions:")
print("1. 10-day momentum <= 0 OR")
print("2. 20-day/10-day volume ratio <= 1 OR")
print("3. RSI > 70 (overbought)")
print("\nDetailed trade analysis can be found in the generated trade log.") 