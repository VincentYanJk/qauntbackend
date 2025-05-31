from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    save_trade_log
)

from Quantlib.strategies.technical_voting3_strategy import Technical_Voting3_Strategy
from Quantlib.backtest.engine import run_backtest

print("Running technical analysis backtest...")
df, trades = run_backtest(
    strategy_class=Technical_Voting3_Strategy,
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=True,
    kwargs={
        'rsi_period': 14,
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'bb_period': 20,
        'bb_devfactor': 2,
        'stoch_period': 14,
        'stoch_dfast': 3,
        'stoch_dslow': 3,
        'williams_period': 14
    }
)

# Visualization and trade logging
plot_equity_curve(df["equity"])
plot_drawdown(df["equity"])
plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
save_trade_log(trades) 