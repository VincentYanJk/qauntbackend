import sys
print(f"Using Python from: {sys.executable}")

from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    save_trade_log
)

from Quantlib.strategies.rsi_bollinger_strategy import RSIBollingerStrategy
from Quantlib.backtest.engine import run_backtest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product
from tqdm import tqdm
import os

# Create directory for saving results if it doesn't exist
save_dir = 'data/optimization_rsi_bollinger'
os.makedirs(save_dir, exist_ok=True)

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
rsi_oversold_levels = range(20, 41, 5)  # 20, 25, 30, 35, 40
rsi_overbought_levels = range(60, 81, 5)  # 60, 65, 70, 75, 80
bb_periods = range(10, 31, 5)  # 10, 15, 20, 25, 30
bb_devfactors = [1.5, 2.0, 2.5, 3.0]  # Standard deviation multipliers

# Store results
results = []

# Calculate total combinations for progress bar
total_combinations = len(list(product(
    rsi_periods, 
    rsi_oversold_levels, 
    rsi_overbought_levels,
    bb_periods,
    bb_devfactors
)))

# Test each parameter combination
print("\nOptimizing RSI + Bollinger Bands parameters...")
progress_bar = tqdm(total=total_combinations, desc="Testing combinations")

for rsi_period, oversold, overbought, bb_period, bb_dev in product(
    rsi_periods, 
    rsi_oversold_levels, 
    rsi_overbought_levels,
    bb_periods,
    bb_devfactors
):
    # Skip invalid RSI level combinations
    if oversold >= overbought:
        progress_bar.update(1)
        continue
        
    try:
        # Run backtest with current parameters
        df, trades_df, performance = run_backtest(
            strategy_class=RSIBollingerStrategy,
            data_path="data/BTC-Daily.csv",
            cash=100000,
            plot=False,
            kwargs={
                'rsi_period': rsi_period,
                'rsi_oversold': oversold,
                'rsi_overbought': overbought,
                'bb_period': bb_period,
                'bb_devfactor': bb_dev,
                'commission_scheme': commission_scheme,
                'slippage_scheme': slippage_scheme,
                'trade_size': 0.5  # Use 50% of portfolio per trade
            }
        )
        
        # Store results
        results.append({
            'rsi_period': rsi_period,
            'rsi_oversold': oversold,
            'rsi_overbought': overbought,
            'bb_period': bb_period,
            'bb_devfactor': bb_dev,
            'total_return': performance.total_return,
            'sharpe_ratio': performance.sharpe_ratio,
            'max_drawdown': performance.max_drawdown,
            'total_trades': performance.total_trades,
            'win_rate': performance.win_rate
        })
        
    except Exception as e:
        print(f"\nError with parameters (RSI Period={rsi_period}, Oversold={oversold}, Overbought={overbought}, BB Period={bb_period}, BB Dev={bb_dev}): {str(e)}")
    
    progress_bar.update(1)

progress_bar.close()

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Save full results to CSV
results_df.to_csv(os.path.join(save_dir, 'rsi_bollinger_optimization_results.csv'), index=False)

# Print best parameters by different metrics
print("\nBest Parameters by Total Return:")
best_return_idx = results_df['total_return'].idxmax()
print(results_df.iloc[best_return_idx])

print("\nBest Parameters by Sharpe Ratio:")
best_sharpe_idx = results_df['sharpe_ratio'].idxmax()
print(results_df.iloc[best_sharpe_idx])

print("\nBest Parameters by Win Rate:")
best_winrate_idx = results_df['win_rate'].idxmax()
print(results_df.iloc[best_winrate_idx])

# Save optimization results to text file
results_txt_path = os.path.join(save_dir, 'optimization_results.txt')
with open(results_txt_path, 'w') as f:
    f.write("Best Parameters by Total Return:\n")
    f.write("---------------------------\n")
    best_return = results_df.iloc[best_return_idx]
    for key, value in best_return.items():
        if key in ['total_return', 'max_drawdown', 'win_rate']:
            f.write(f"{key:15}: {value:.6f}\n")
        else:
            f.write(f"{key:15}: {value:.6f}\n")
    
    f.write("\nBest Parameters by Sharpe Ratio:\n")
    f.write("------------------------------\n")
    best_sharpe = results_df.iloc[best_sharpe_idx]
    for key, value in best_sharpe.items():
        if key in ['total_return', 'max_drawdown', 'win_rate']:
            f.write(f"{key:15}: {value:.6f}\n")
        else:
            f.write(f"{key:15}: {value:.6f}\n")
    
    f.write("\nBest Parameters by Win Rate:\n")
    f.write("--------------------------\n")
    best_winrate = results_df.iloc[best_winrate_idx]
    for key, value in best_winrate.items():
        if key in ['total_return', 'max_drawdown', 'win_rate']:
            f.write(f"{key:15}: {value:.6f}\n")
        else:
            f.write(f"{key:15}: {value:.6f}\n")

print(f"\nOptimization results have been saved to: {results_txt_path}")

# Create heatmaps for different metrics
def create_heatmap(data, metric, rsi_param='rsi_period', bb_param='bb_period'):
    pivot_table = data.pivot_table(
        values=metric,
        index=rsi_param,
        columns=bb_param,
        aggfunc='mean'
    )
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_table, annot=True, cmap='RdYlGn', center=0)
    plt.title(f'{metric} Heatmap ({rsi_param} vs {bb_param})')
    plt.savefig(os.path.join(save_dir, f'heatmap_{metric}_{rsi_param}_{bb_param}.png'))
    plt.close()

# Generate various heatmaps
metrics = ['total_return', 'sharpe_ratio', 'win_rate']
params = [('rsi_period', 'bb_period'), ('rsi_oversold', 'bb_devfactor'), 
          ('rsi_overbought', 'bb_devfactor')]

for metric in metrics:
    for param1, param2 in params:
        create_heatmap(results_df, metric, param1, param2)

print("\nOptimization completed! Results and heatmaps saved in:", save_dir) 


# Best Parameters by Total Return:
# rsi_period         25.000000
# rsi_oversold       35.000000
# rsi_overbought     80.000000
# bb_period          10.000000
# bb_devfactor        2.500000
# total_return      185.015298
# sharpe_ratio        1.680978
# max_drawdown        0.000000
# total_trades        7.000000
# win_rate            1.000000
# Name: 2382, dtype: float64

# Best Parameters by Sharpe Ratio:
# rsi_period          20.000000
# rsi_oversold        20.000000
# rsi_overbought      60.000000
# bb_period           10.000000
# bb_devfactor         2.500000
# total_return       133.051838
# sharpe_ratio      4173.931683
# max_drawdown         0.000000
# total_trades         3.000000
# win_rate             1.000000

# Best Parameters by Win Rate:
# rsi_period        15.000000
# rsi_oversold      25.000000
# rsi_overbought    75.000000
# bb_period         15.000000
# bb_devfactor       3.000000
# total_return      10.477672
# sharpe_ratio       0.648198
# max_drawdown       0.000000
# total_trades       5.000000
# win_rate           1.000000
