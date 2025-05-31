from Quantlib.backtest.engine import run_backtest
from Quantlib.strategies.rsi_reversion import RSIReversion
from Quantlib.strategies.trend_following import TrendFollowing
from Quantlib.strategies.bollinger_band import BollingerBand
from Quantlib.strategies.macd_crossover import MACDCrossover
from Quantlib.strategies.ml_signal_strategy import MLSignalStrategy

strategy_list = [
    ("RSI Reversion", lambda: RSIReversion(trade_size=0.1)),
    ("Trend Following", lambda: TrendFollowing(trade_size=0.1)),
    ("Bollinger Band", lambda: BollingerBand(trade_size=0.1)),
    ("MACD Crossover", lambda: MACDCrossover(trade_size=0.1)),
    ("ML - XGBoost", lambda: MLSignalStrategy(use_ml=True, model_type="xgboost", trade_size=0.1)),
    ("ML - LSTM", lambda: MLSignalStrategy(use_ml=True, model_type="lstm", trade_size=0.1)),
]

for name, strategy in strategy_list:
    print(f"\n🚀 Running backtest for: {name}")
    run_backtest(
        strategy_class=strategy,
        data_path="data/BTCUSDT.csv",
        cash=100000,
        plot=False
    )