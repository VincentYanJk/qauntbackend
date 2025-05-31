"""
Test a single trading strategy with detailed analysis
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
import argparse

STRATEGIES = {
    'sma': (SMACrossover, {'trade_size': 0.1}),
    'rsi': (RSIReversion, {'trade_size': 0.1}),
    'bb': (BollingerBand, {'trade_size': 0.1}),
    'macd': (MACDCrossover, {'trade_size': 0.1}),
    'xgboost': (MLSignalStrategy, {'use_ml': True, 'model_type': 'xgboost', 'trade_size': 0.1}),
    'lstm': (MLSignalStrategy, {'use_ml': True, 'model_type': 'lstm', 'trade_size': 0.1}),
    'trend': (TrendFollowing, {'trade_size': 0.1})
}

def main():
    parser = argparse.ArgumentParser(description='Test a single trading strategy')
    parser.add_argument('strategy', choices=STRATEGIES.keys(), help='Strategy to test')
    parser.add_argument('--cash', type=float, default=100000, help='Initial cash')
    parser.add_argument('--data', default='data/BTC-Daily.csv', help='Data file path')
    args = parser.parse_args()
    
    strategy_class, kwargs = STRATEGIES[args.strategy]
    print(f"\n🚀 Testing {args.strategy} strategy...")
    
    df, trades = run_backtest(
        strategy_class=strategy_class,
        data_path=args.data,
        cash=args.cash,
        plot=True,
        kwargs=kwargs
    )
    
    # Analysis
    plot_equity_curve(df["equity"])
    plot_drawdown(df["equity"])
    plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
    save_trade_log(trades)
    
    # Print summary
    final_equity = df["equity"][-1]
    roi = (final_equity - args.cash) / args.cash * 100
    print(f"\n📊 Results:")
    print(f"Initial Cash: ${args.cash:,.2f}")
    print(f"Final Equity: ${final_equity:,.2f}")
    print(f"ROI: {roi:.2f}%")

if __name__ == "__main__":
    main()