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
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product
from tqdm import tqdm
import os

# Create directory for saving heatmaps if it doesn't exist
save_dir = 'data/optimization_mfi'
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
    'slip_open': True,  # Apply slippage on open positions
}

# Define parameter ranges for optimization
periods = range(5, 31, 5)  # 5, 10, 15, 20, 25, 30
oversold_levels = range(20, 41, 5)  # 20, 25, 30, 35, 40
overbought_levels = range(60, 81, 5)  # 60, 65, 70, 75, 80

# Store results
results = []

# Run optimization
for period, oversold, overbought in tqdm(list(product(periods, oversold_levels, overbought_levels))):
    # Skip invalid combinations
    if oversold >= overbought:
        continue
        
    # Run backtest with current parameters
    df, trades_df, performance = run_backtest(
        strategy_class=MFIStrategy,
        data_path="data/BTC-Daily.csv",
        cash=100000,
        plot=False,
        kwargs={
            'trade_size': 0.5,  # Use 50% of portfolio per trade
            'period': period,
            'oversold': oversold,
            'overbought': overbought,
            'commission_scheme': commission_scheme,
            'slippage_scheme': slippage_scheme
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

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Find best parameters by different metrics
best_return = results_df.loc[results_df['total_return'].idxmax()]
best_sharpe = results_df.loc[results_df['sharpe_ratio'].idxmax()]
best_drawdown = results_df.loc[results_df['max_drawdown'].idxmax()]

# Define metrics to display
metrics = {
    'Total Return': best_return,
    'Sharpe Ratio': best_sharpe
}

# Parameters to display
params = [
    ('period', ''),
    ('oversold', ''),
    ('overbought', ''),
    ('total_return', '%'),
    ('sharpe_ratio', ''),
    ('max_drawdown', '%'),
    ('total_trades', '')
]

# Print results for each metric
for metric_name, result in metrics.items():
    print(f"\nBest Parameters by {metric_name}:")
    for param, suffix in params:
        value = result[param]
        if param in ['total_return', 'sharpe_ratio', 'max_drawdown']:
            print(f"{param.replace('_', ' ').title()}: {value:.2f}{suffix}")
        else:
            print(f"{param.replace('_', ' ').title()}: {value}{suffix}")

# Print results for best return parameters
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

# Generate heatmaps for different metrics and periods
print("\nGenerating heatmaps...")
for metric in ['total_return', 'sharpe_ratio', 'max_drawdown']:
    for period in periods:
        period_data = results_df[results_df['period'] == period]
        if not period_data.empty:
            plt.figure(figsize=(12, 8))
            pivot = period_data.pivot(index='oversold', columns='overbought', values=metric)
            
            # Choose appropriate colormap and format
            if metric == 'max_drawdown':
                cmap = 'RdYlGn_r'  # Reversed colormap for drawdown (red is bad)
            else:
                cmap = 'RdYlGn'    # Regular colormap (green is good)
            
            # Format values appropriately
            fmt = '.2%' if metric in ['total_return', 'max_drawdown'] else '.2f'
            
            # Create heatmap
            sns.heatmap(pivot, annot=True, fmt=fmt, cmap=cmap, center=0,
                       cbar_kws={'label': metric.replace('_', ' ').title()})
            
            plt.title(f'MFI {metric.replace("_", " ").title()} (Period: {period})')
            plt.xlabel('Overbought Level')
            plt.ylabel('Oversold Level')
            
            # Save the plot
            plt.savefig(os.path.join(save_dir, f'mfi_{metric}_period_{period}_heatmap.png'), bbox_inches='tight', dpi=300)
            plt.close()

print(f"Heatmaps have been saved in {save_dir} directory.")

# Run final backtest with best Sharpe parameters and generate plots
df, trades_df, performance = run_backtest(
    strategy_class=MFIStrategy,
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=True,
    kwargs={
        'trade_size': 0.5,
        'period': int(best_sharpe['period']),
        'oversold': int(best_sharpe['oversold']),
        'overbought': int(best_sharpe['overbought']),
        'commission_scheme': commission_scheme,
        'slippage_scheme': slippage_scheme
    }
)

# Print all performance metrics for best parameters
print("\nDetailed Performance for Best Sharpe Parameters:")
performance.print_all()

# Generate plots
plot_equity_curve(df["equity"])
plot_drawdown(df["equity"])
plot_signals(df, df.get("buy_signal"), df.get("sell_signal")) 