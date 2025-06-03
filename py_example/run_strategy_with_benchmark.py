import sys
print(f"Using Python from: {sys.executable}")

from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    save_trade_log
)

from Quantlib.strategies import SMACrossover, BuyAndHoldStrategy
from Quantlib.backtest.engine import run_backtest
import pandas as pd
import matplotlib.pyplot as plt

# Define commission and slippage settings
commission_scheme = {
    'commission': 0.002,  # 0.2% trading fee
    'margin': None,  # No margin trading
    'mult': 1.0,  # No leverage
}

# Define slippage settings
slippage_scheme = {
    'slip_perc': 0.001,  # 0.1% slippage
    'slip_fixed': 0.0,  # No fixed slippage
    'slip_open': True,  # Apply slippage on open orders
}

print("\nRunning Buy & Hold strategy first...")
# Run buy-and-hold benchmark first
df_benchmark, trades_df_benchmark, performance_benchmark = run_backtest(
    strategy_class=BuyAndHoldStrategy,
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=False,
    kwargs={
        'trade_size': 1.0,  # Use 100% of portfolio for buy & hold
        'commission_scheme': commission_scheme,
        'slippage_scheme': slippage_scheme
    }
)

print("\nRunning SMA Crossover strategy...")
# Run strategy backtest
df_strategy, trades_df_strategy, performance_strategy = run_backtest(
    strategy_class=SMACrossover,
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=False,
    kwargs={
        'trade_size': 0.3,  # Use 30% of portfolio per trade
        'commission_scheme': commission_scheme,
        'slippage_scheme': slippage_scheme
    }
)

# Print performance comparisons
print("\n=== Buy & Hold Performance ===")
performance_benchmark.print_all()

print("\n=== Strategy Performance ===")
performance_strategy.print_all()

# Calculate relative performance
relative_return = (performance_strategy.total_return - performance_benchmark.total_return)
print(f"\n=== Relative Performance ===")
print(f"Strategy vs Buy & Hold: {relative_return:.2%}")

# Plot comparison of equity curves
plt.figure(figsize=(12, 6))
plt.plot(df_benchmark.index, df_benchmark['equity'], label='Buy & Hold', linewidth=2)
plt.plot(df_strategy.index, df_strategy['equity'], label='SMA Strategy', linewidth=2)
plt.title('Strategy vs Buy & Hold Performance')
plt.xlabel('Date')
plt.ylabel('Portfolio Value ($)')
plt.legend()
plt.grid(True)
plt.show()

# Save trade logs
print("\nSaving trade logs...")
save_trade_log(trades_df_strategy, output_path='strategy_trades.csv')
save_trade_log(trades_df_benchmark, output_path='benchmark_trades.csv') 