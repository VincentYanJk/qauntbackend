import sys
print(f"Using Python from: {sys.executable}")

from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    save_trade_log
)

from Quantlib.strategies.rsi_reversion import RSIReversion
from Quantlib.backtest.engine import run_backtest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product
from tqdm import tqdm

# Define commission and slippage settings
commission_scheme = {
    'commission': 0.002,  # 0.2% trading fee
    'margin': None,  # No margin trading
    'mult': 1.0,  # No leverage
}

slippage_scheme = {
    'slip_perc': 0.001,  # 0.1% slippage
    'slip_fixed': 0.0,  # No fixed slippage
    'slip_open': True,  # Apply slippage on open orders
}

# Define parameter ranges
rsi_periods = range(5, 31, 5)  # 5, 10, 15, 20, 25, 30
oversold_levels = range(20, 41, 5)  # 20, 25, 30, 35, 40
overbought_levels = range(60, 81, 5)  # 60, 65, 70, 75, 80

# Store results
results = []

# Test each parameter combination
print("\nOptimizing RSI parameters...")
total_combinations = len(list(product(rsi_periods, oversold_levels, overbought_levels)))
progress_bar = tqdm(total=total_combinations, desc="Testing combinations")

for period, oversold, overbought in product(rsi_periods, oversold_levels, overbought_levels):
    # Skip invalid combinations where oversold >= overbought
    if oversold >= overbought:
        progress_bar.update(1)
        continue
        
    try:
        # Run backtest with current parameters
        df, trades_df, performance = run_backtest(
            strategy_class=RSIReversion,
            data_path="data/BTC-Daily.csv",
            cash=100000,
            plot=False,
            kwargs={
                'period': period,
                'oversold': oversold,
                'overbought': overbought,
                'commission_scheme': commission_scheme,
                'slippage_scheme': slippage_scheme,
                'trade_size': 0.5  # Use 50% of portfolio per trade
            }
        )
        
        # Store results
        results.append({
            'period': period,
            'oversold': oversold,
            'overbought': overbought,
            'total_return': performance.total_return,
            'sharpe_ratio': performance.sharpe_ratio,
            'max_drawdown': performance.max_drawdown,
            'total_trades': performance.total_trades
        })
        
    except Exception as e:
        print(f"\nError with parameters (period={period}, oversold={oversold}, overbought={overbought}): {str(e)}")
    
    progress_bar.update(1)

progress_bar.close()

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Save optimization results to CSV
results_df.to_csv('rsi_optimization_results.csv', index=False)

# Create heatmaps for different period slices
for metric in ['total_return', 'sharpe_ratio', 'max_drawdown']:
    for period in rsi_periods:
        period_data = results_df[results_df['period'] == period]
        if not period_data.empty:
            plt.figure(figsize=(12,8))
            pivot = period_data.pivot(index='oversold', columns='overbought', values=metric)
            fmt = '.2%' if metric in ['total_return', 'max_drawdown'] else '.2f'
            sns.heatmap(pivot, annot=True, fmt=fmt, cmap='RdYlGn', center=0)
            plt.title(f'{metric.replace("_", " ").title()} (RSI Period: {period})')
            plt.savefig(f'rsi_{metric}_period_{period}_heatmap.png')
            plt.close()

# Find best parameters by different metrics
best_return = results_df.loc[results_df['total_return'].idxmax()]
best_sharpe = results_df.loc[results_df['sharpe_ratio'].idxmax()]
max_trades = results_df.loc[results_df['total_trades'].idxmax()]
best_drawdown = results_df.loc[results_df['max_drawdown'].idxmin()]

# Print results
print("\n=== Best Parameters by Total Return ===")
for key, value in best_return.items():
    if key in ['total_return', 'max_drawdown']:
        print(f"{key}: {value:.2%}")
    else:
        print(f"{key}: {value:.2f}")

print("\n=== Best Parameters by Sharpe Ratio ===")
for key, value in best_sharpe.items():
    if key in ['total_return', 'max_drawdown']:
        print(f"{key}: {value:.2%}")
    else:
        print(f"{key}: {value:.2f}")

print("\n=== Best Parameters by Max Drawdown ===")
for key, value in best_drawdown.items():
    if key in ['total_return', 'max_drawdown']:
        print(f"{key}: {value:.2%}")
    else:
        print(f"{key}: {value:.2f}")

print("\n=== Best Parameters by Total Trades ===")
for key, value in max_trades.items():
    if key in ['total_return', 'max_drawdown']:
        print(f"{key}: {value:.2%}")
    else:
        print(f"{key}: {value:.2f}") 