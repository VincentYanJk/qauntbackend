"""
Compare performance of multiple trading strategies
"""
import sys
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt

from Quantlib.visualization.visualize import plot_equity_curve
from Quantlib.backtest.engine import run_backtest

# Import all strategies
from Quantlib.strategies.buy_and_hold import BuyAndHoldStrategy
from Quantlib.strategies.momentum_sma_strategy import MomentumSMAStrategy
from Quantlib.strategies.momentum_vol_rsi_strategy import MomentumVolRSIStrategy
from Quantlib.strategies.multi_filter_strategy import MultiFilterStrategy

# Common settings for all strategies
INITIAL_CASH = 100000
DATA_PATH = "data/BTC-Daily.csv"

commission_scheme = {
    'commission': 0.002,  # 0.2% trading fee
    'margin': None,
    'mult': 1.0,
}

slippage_scheme = {
    'slip_perc': 0.001,  # 0.1% slippage
    'slip_fixed': 0.0,
    'slip_open': True,
}

# Define strategies and their parameters
strategies = {
    "Buy & Hold": {
        "class": BuyAndHoldStrategy,
        "params": {
            "trade_size": 0.5
        }
    },
    "Momentum-SMA": {
        "class": MomentumSMAStrategy,
        "params": {
            "momentum_period": 5,
            "sma_period": 20,
            "trade_size": 0.5
        }
    },
    "Momentum-Vol-RSI": {
        "class": MomentumVolRSIStrategy,
        "params": {
            "momentum_period": 5,
            "vol_short_period": 5,
            "vol_long_period": 10,
            "rsi_period": 14,
            "momentum_threshold": 0,
            "vol_ratio_threshold": 0,
            "rsi_lower": 30,
            "rsi_upper": 70,
            "trade_size": 0.5
        }
    },
    "Multi-Filter": {
        "class": MultiFilterStrategy,
        "params": {
            "momentum_period": 5,
            "sma_period": 20,
            "volume_period": 10,
            "atr_period": 14,
            "atr_threshold": 0.05,
            "rsi_period": 14,
            "rsi_threshold": 70,
            "trade_size": 0.5
        }
    }
}

# Run backtests and collect results
results = {}
equity_curves = {}

print("Running backtests...")
for name, strategy in strategies.items():
    print(f"\nTesting {name} strategy...")
    
    # Add common parameters
    params = {
        **strategy["params"],
        "commission_scheme": commission_scheme,
        "slippage_scheme": slippage_scheme
    }
    
    # Run backtest
    df, trades_df, performance = run_backtest(
        strategy_class=strategy["class"],
        data_path=DATA_PATH,
        cash=INITIAL_CASH,
        plot=False,
        kwargs=params
    )
    
    # Store results
    results[name] = {
        "Total Return (%)": performance.total_return * 100,
        "Sharpe Ratio": performance.sharpe_ratio,
        "Max Drawdown (%)": performance.max_drawdown * 100,
        "Win Rate (%)": performance.win_rate * 100,
        "Trades": len(trades_df)
    }
    equity_curves[name] = df["equity"]

# Create performance comparison table
df_results = pd.DataFrame(results).T
df_results = df_results.round(2)

# Sort by Sharpe Ratio
df_results_sorted = df_results.sort_values("Sharpe Ratio", ascending=False)

# Print results
print("\nPerformance Comparison:")
print(tabulate(df_results_sorted, headers="keys", tablefmt="pipe", floatfmt=".2f"))

# Plot equity curves
plt.figure(figsize=(12, 6))
for name, equity in equity_curves.items():
    plt.plot(equity.index, equity.values, label=name)

plt.title("Strategy Comparison - Equity Curves")
plt.xlabel("Date")
plt.ylabel("Portfolio Value ($)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("strategy_comparison.png")
plt.close()

# Find best strategy for each metric
best_sharpe = df_results_sorted.index[0]
best_return = df_results_sorted["Total Return (%)"].idxmax()
best_drawdown = df_results_sorted["Max Drawdown (%)"].idxmin()

print("\nBest Strategies by Metric:")
print(f"Best Sharpe Ratio: {best_sharpe} ({df_results_sorted.loc[best_sharpe, 'Sharpe Ratio']:.2f})")
print(f"Best Total Return: {best_return} ({df_results_sorted.loc[best_return, 'Total Return (%)']:.2f}%)")
print(f"Lowest Max Drawdown: {best_drawdown} ({df_results_sorted.loc[best_drawdown, 'Max Drawdown (%)']:.2f}%)")

# Overall recommendation
print("\nOverall Analysis:")
print(f"Based on the combination of Sharpe ratio, total return, and maximum drawdown,")
print(f"the {best_sharpe} strategy appears to be the most robust choice with:")
print(f"- Sharpe Ratio: {df_results_sorted.loc[best_sharpe, 'Sharpe Ratio']:.2f}")
print(f"- Total Return: {df_results_sorted.loc[best_sharpe, 'Total Return (%)']:.2f}%")
print(f"- Max Drawdown: {df_results_sorted.loc[best_sharpe, 'Max Drawdown (%)']:.2f}%")
print(f"- Number of Trades: {df_results_sorted.loc[best_sharpe, 'Trades']:.0f}")
print(f"- Win Rate: {df_results_sorted.loc[best_sharpe, 'Win Rate (%)']:.2f}%")

print("\nEquity curves comparison has been saved as 'strategy_comparison.png'") 