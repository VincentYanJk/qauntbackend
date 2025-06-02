# %% [markdown]
# # SMA Crossover Strategy Backtest
# 
# This notebook demonstrates how to implement and backtest a Simple Moving Average (SMA) crossover strategy using the Quantlib framework.
#
# ## Strategy Overview
# The SMA crossover strategy is a trend-following strategy that generates trading signals based on the intersection of two moving averages:
# - Buy when the shorter-term SMA crosses above the longer-term SMA
# - Sell when the shorter-term SMA crosses below the longer-term SMA
#
# We'll also include realistic trading costs:
# - Commission: 0.2% per trade (typical for crypto exchanges)
# - Slippage: 0.1% (conservative estimate for liquid markets)

# %% [markdown]
# ## Setup and Imports
# First, let's import the necessary modules and check our Python environment:

# %%
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
import os
import pandas as pd

# Add parent directory to Python path
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# %% [markdown]
# ## Configure Trading Costs
# 
# Let's set up our commission and slippage parameters to make the backtest more realistic:

# %%
# Define commission and slippage settings
commission_scheme = {
    'commission': 0.002,  # 0.2% trading fee
    'margin': None,      # No margin trading
    'mult': 1.0,        # No leverage
}

slippage_scheme = {
    'slip_perc': 0.001,  # 0.1% slippage
    'slip_fixed': 0.0,   # No fixed slippage
    'slip_open': True,   # Apply slippage on open orders
}

# %% [markdown]
# ## Running the Backtest
# 
# Now we'll run the backtest with the following parameters:
# - Initial capital: $100,000
# - Trade size: 10% of portfolio per trade
# - Data: BTC daily prices
#
# First, let's verify our data:

# %%
# Verify data file exists and peek at the data
data_path = "../data/BTC-Daily.csv"
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Data file not found at {data_path}. Please check the file path.")

# Read first few rows of data
df_preview = pd.read_csv(data_path, nrows=5)
print("Preview of the data:")
print(df_preview)
print("\nColumns available:", df_preview.columns.tolist())

# %% [markdown]
# Now that we've verified our data, let's run the backtest with trading costs:

# %%
print("Running backtest...")
df, trades = run_backtest(
    strategy_class=SMACrossover,  # Using SMACrossover strategy class
    data_path=data_path,
    cash=100000,
    plot=True,
    kwargs={
        'trade_size': 0.1,  # Trading with 10% of portfolio
        'commission_scheme': commission_scheme,  # Add commission settings
        'slippage_scheme': slippage_scheme  # Add slippage settings
    }
)
print("\nBacktest completed successfully!")

# %% [markdown]
# ## Analyzing Results
# Let's examine the backtest results through different visualizations:
#
# ### 1. Performance Metrics

# %%
# Calculate and display key metrics
initial_capital = 100000
final_capital = df['equity'].iloc[-1]
total_return = (final_capital - initial_capital) / initial_capital * 100
n_trades = len(trades)
win_rate = len([t for t in trades if t['pnl'] > 0]) / n_trades * 100 if n_trades > 0 else 0

print("=== Performance Summary ===")
print(f"Initial Capital: ${initial_capital:,.2f}")
print(f"Final Capital: ${final_capital:,.2f}")
print(f"Total Return: {total_return:.2f}%")
print(f"Total Trades: {n_trades}")
print(f"Win Rate: {win_rate:.2f}%")
print("========================")

# %% [markdown]
# ### 2. Equity Curve
# The equity curve shows how our portfolio value changes over time:

# %%
print("Plotting equity curve...")
plot_equity_curve(df["equity"])

# %% [markdown]
# ### 3. Drawdown Analysis
# The drawdown chart helps us understand the risk profile of our strategy:

# %%
print("Plotting drawdown...")
plot_drawdown(df["equity"])

# %% [markdown]
# ### 4. Trade Signals
# Let's visualize when the strategy entered and exited positions:

# %%
print("Plotting trade signals...")
plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))

# %% [markdown]
# ### 5. Trade Log
# Finally, let's save the detailed trade log for further analysis:

# %%
print("Saving trade log...")
save_trade_log(trades)

# Show the first few trades
trades_df = pd.DataFrame(trades)
if not trades_df.empty:
    print("\nFirst 5 trades:")
    print(trades_df.head())

# %% [markdown]
# ## Next Steps
# 
# To improve the strategy, you might want to:
# 1. Adjust the SMA periods
# 2. Modify the position sizing
# 3. Add stop-loss and take-profit rules
# 4. Test on different timeframes or assets 