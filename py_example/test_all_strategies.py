"""
Comprehensive test suite for all trading strategies
"""
from Quantlib.strategies import (
    SMACrossover,
    RSIReversion,
    BollingerBand,
    MACDCrossover,
    MLSignalStrategy,
    TrendFollowing
)
from Quantlib.backtest.engine import run_backtest
from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    save_trade_log
)
from Quantlib.forecast import train_model
import os

def test_strategy(strategy_class, name, **kwargs):
    """Run backtest for a single strategy"""
    print(f"\n🚀 Testing {name} Strategy...")
    
    df, trades = run_backtest(
        strategy_class=strategy_class,
        data_path="data/BTC-Daily.csv",
        cash=100000,
        plot=True,
        kwargs=kwargs
    )
    
    print(f"\n📊 Results for {name}:")
    plot_equity_curve(df["equity"])
    plot_drawdown(df["equity"])
    plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
    save_trade_log(trades)
    
    return df["equity"][-1]  # Return final equity

def main():
    """Run tests for all strategies"""
    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)
    
    # First train ML models
    print("\n🧠 Training ML models...")
    train_model(
        df_path="data/BTC-Daily.csv",
        model_type="xgboost",
        save_path="models/xgb_model.pkl"
    )
    
    train_model(
        df_path="data/BTC-Daily.csv",
        model_type="lstm",
        save_path="models/lstm_model.pt"
    )
    
    # Test all strategies
    results = []
    strategies = [
        (SMACrossover, "SMA Crossover", {'trade_size': 0.1}),
        (RSIReversion, "RSI Reversion", {'trade_size': 0.1}),
        (BollingerBand, "Bollinger Bands", {'trade_size': 0.1}),
        (MACDCrossover, "MACD Crossover", {'trade_size': 0.1}),
        (MLSignalStrategy, "XGBoost", {'use_ml': True, 'model_type': 'xgboost', 'trade_size': 0.1}),
        (MLSignalStrategy, "LSTM", {'use_ml': True, 'model_type': 'lstm', 'trade_size': 0.1}),
        (TrendFollowing, "Trend Following", {'trade_size': 0.1})
    ]
    
    for strategy_class, name, kwargs in strategies:
        final_equity = test_strategy(strategy_class, name, **kwargs)
        results.append((name, final_equity))
    
    # Print summary
    print("\n📈 Strategy Performance Summary:")
    print("-" * 40)
    for name, equity in results:
        roi = (equity - 100000) / 100000 * 100
        print(f"{name:20} ROI: {roi:8.2f}%")

if __name__ == "__main__":
    main()