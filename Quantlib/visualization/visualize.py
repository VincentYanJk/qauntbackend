import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def plot_equity_curve(equity_series):
    plt.figure(figsize=(12, 4))
    plt.plot(equity_series, label="Equity Curve")
    plt.title("Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid()
    plt.show()

def plot_drawdown(equity_series):
    peak = equity_series.cummax()
    drawdown = (equity_series - peak) / peak
    plt.figure(figsize=(12, 4))
    plt.plot(drawdown, label="Drawdown")
    plt.title("Drawdown")
    plt.xlabel("Time")
    plt.ylabel("Drawdown (%)")
    plt.legend()
    plt.grid()
    plt.show()

def plot_factor_exposures(df):
    plt.figure(figsize=(12, 4))
    df.plot(kind="line")
    plt.title("Factor Exposures Over Time")
    plt.xlabel("Time")
    plt.grid()
    plt.tight_layout()
    plt.show()

def plot_signals(data, buy_signals=None, sell_signals=None):
    plt.figure(figsize=(12, 4))
    plt.plot(data.index, data["close"], label="Close Price")
    
    # Plot buy signals
    if buy_signals is not None:
        buy_points = data[buy_signals.notnull()].index
        buy_prices = data.loc[buy_points, "close"]
        plt.scatter(buy_points, buy_prices, marker="^", color="green", s=100, label="Buy")
    
    # Plot sell signals
    if sell_signals is not None:
        sell_points = data[sell_signals.notnull()].index
        sell_prices = data.loc[sell_points, "close"]
        plt.scatter(sell_points, sell_prices, marker="v", color="red", s=100, label="Sell")
    
    plt.title("Price and Signals")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    plt.show()

def plot_trade_returns(trades_df):
    """
    Plot the distribution of trade returns with color-coded points.
    
    Parameters:
    -----------
    trades_df : pandas.DataFrame
        DataFrame containing trade information with pnlcomm column
        showing the profit/loss after commission for each trade
    """
    # Get unique trades by filtering only buy signals (to avoid counting both entry and exit)
    buy_trades = trades_df[trades_df['type'] == 'buy']
    
    # Use pnlcomm for returns as it includes commission
    returns = buy_trades['pnlcomm'].values
    n = len(returns)
    
    plt.figure(figsize=(10, 5))
    plt.scatter(range(n), returns, c=returns, cmap='RdYlGn', s=80, edgecolor='k')
    plt.axhline(0, color='gray', linestyle='--', lw=1)
    plt.title('Trade Return Distribution')
    plt.xlabel('Trade Number')
    plt.ylabel('Profit/Loss after Commission')
    plt.colorbar(label='P&L')
    
    # Add summary statistics
    avg_return = returns.mean()
    win_rate = (returns > 0).mean() * 100
    plt.text(0.02, 0.95, f'Average P&L: ${avg_return:.2f}\nWin Rate: {win_rate:.1f}%', 
             transform=plt.gca().transAxes, 
             bbox=dict(facecolor='white', alpha=0.8))
    
    plt.grid(True, alpha=0.3)
    plt.show()

def save_trade_log(trades, output_path="trades_log.csv"):
    trades.to_csv(output_path, index=False)
    print(f"✅ Trade log saved to: {output_path}")