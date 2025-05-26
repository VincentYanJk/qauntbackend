import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
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
    plt.plot(data["close"], label="Close Price")
    if buy_signals is not None:
        plt.plot(buy_signals.index, buy_signals, "^", label="Buy", color="green", markersize=8)
    if sell_signals is not None:
        plt.plot(sell_signals.index, sell_signals, "v", label="Sell", color="red", markersize=8)
    plt.title("Price and Signals")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    plt.show()

def save_trade_log(trades, output_path="trades_log.csv"):
    trades.to_csv(output_path, index=False)
    print(f"✅ Trade log saved to: {output_path}")