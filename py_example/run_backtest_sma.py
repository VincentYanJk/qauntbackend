import sys
print(f"Using Python from: {sys.executable}")

from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    save_trade_log
)

from Quantlib.strategies.sma_crossover import SMACrossover
from Quantlib.backtest.engine import run_backtest
import sys, os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

df, trades = run_backtest(
    strategy_class=SMACrossover,  # Remove lambda, use direct class reference
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=True,
    kwargs={
        'trade_size': 0.1,  # Trading with 10% of portfolio
        'commission_scheme': commission_scheme,  # Add commission settings
        'slippage_scheme': slippage_scheme  # Add slippage settings
    }
)

print("finish-finish----1")
# Visualization and trade logging
plot_equity_curve(df["equity"])
print("finish-finish----2")
plot_drawdown(df["equity"])
print("finish-finish----3")
plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
print("finish-finish----4")
save_trade_log(trades)
print("finish-finish----5")