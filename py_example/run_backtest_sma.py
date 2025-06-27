import sys
print(f"Using Python from: {sys.executable}")

from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    plot_trade_returns,
    save_trade_log
)

from Quantlib.strategies.sma_crossover import SMACrossover
from Quantlib.backtest.engine import run_backtest
import sys

# Define commission and slippage settings
commission_scheme = {
    'commission': 0.002,  # 0.1% trading fee (typical for crypto exchanges)
    'margin': None,  # No margin trading
    'mult': 1.0,  # No leverage
}

# Define slippage settings
slippage_scheme = {
    'slip_perc': 0.001,  # 0.1% slippage (conservative estimate)
    'slip_fixed': 0.0,  # No fixed slippage
    'slip_open': True,  # Apply slippage on open orders
}

# Run backtest
df, trades_df, performance = run_backtest(
    strategy_class=SMACrossover,
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=True,
    kwargs={
        'trade_size':0.5,  # Use 10% of portfolio per trade
        'commission_scheme': commission_scheme,
        'slippage_scheme': slippage_scheme
    }
)

# Print all performance metrics
performance.print_all()

# Or print specific metrics you're interested in
# print("\nKey Metrics:")
# print(f"Total Return: {performance.total_return:.2%}")
# print(f"Sharpe Ratio: {performance.sharpe_ratio:.4f}")
# print(f"Win Rate: {performance.win_rate:.2%}")

# Visualization and trade logging
plot_equity_curve(df["equity"])
print("finish-finish----2")
plot_drawdown(df["equity"])
print("finish-finish----3")
plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
print("finish-finish----4")
# Add trade returns distribution plot
plot_trade_returns(trades_df)
print("finish-finish----5")
save_trade_log(trades_df)
print("finish-finish----6")