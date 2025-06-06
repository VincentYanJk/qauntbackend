import sys
print(f"Using Python from: {sys.executable}")

from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    save_trade_log
)

from Quantlib.strategies.mfi_strategy import MFIStrategy
from Quantlib.backtest.engine import run_backtest

# Define commission and slippage settings
commission_scheme = {
    'commission': 0.002,  # 0.2% trading fee (typical for crypto exchanges)
    'margin': None,  # No margin trading
    'mult': 1.0,  # No leverage
}

# Define slippage settings
slippage_scheme = {
    'slip_perc': 0.001,  # 0.1% slippage (conservative estimate)
    'slip_fixed': 0.0,  # No fixed slippage
    'slip_open': True,  # Apply slippage on open orders
}

# Run backtest with MFI strategy
df, trades_df, performance = run_backtest(
    strategy_class=MFIStrategy,
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=True,
    kwargs={
        'trade_size': 0.5,  # Use 50% of portfolio per trade
        'period': 14,  # MFI period
        'oversold': 20,  # MFI oversold threshold
        'overbought': 80,  # MFI overbought threshold
        'commission_scheme': commission_scheme,
        'slippage_scheme': slippage_scheme
    }
)

# Print all performance metrics
performance.print_all()

# Visualization and trade logging
plot_equity_curve(df["equity"])
plot_drawdown(df["equity"])
plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
save_trade_log(trades_df) 