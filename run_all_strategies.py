from Quantlib.backtest.engine import run_backtest
from Quantlib.strategies.rsi_reversion import RSIReversion
from Quantlib.strategies.trend_following import TrendFollowing
from Quantlib.strategies.bollinger_band import BollingerBand
from Quantlib.strategies.macd_crossover import MACDCrossover
from Quantlib.strategies.ml_signal_strategy import MLSignalStrategy

strategy_list = [
    ("RSI Reversion", RSIReversion),
    ("Trend Following", TrendFollowing),
    ("Bollinger Band", BollingerBand),
    ("MACD Crossover", MACDCrossover),
    ("ML - XGBoost", lambda: MLSignalStrategy(use_ml=True, model_type="xgboost")),
    ("ML - LSTM", lambda: MLSignalStrategy(use_ml=True, model_type="lstm")),
]

for name, strategy in strategy_list:
    print(f"\n🚀 Running backtest for: {name}")
    run_backtest(
        strategy_class=strategy,
        data_path="data/BTCUSDT.csv",
        cash=100000,
        plot=False
    )