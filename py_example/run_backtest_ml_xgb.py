from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    plot_trade_returns,
    save_trade_log
)

from Quantlib.strategies.ml_signal_strategy import MLSignalStrategy
from Quantlib.backtest.engine import run_backtest
from Quantlib.forecast import load_model, train_model
from Quantlib.forecast.features import list_available_features
import os
import pandas as pd
import matplotlib.pyplot as plt

# Ensure models directory exists
os.makedirs("models", exist_ok=True)

MODEL_TYPE = "xgboost"
MODEL_PATH = f"models/{MODEL_TYPE}_model.pkl"

# Define feature configuration
feature_config = {
    'returns': {'periods': [1, 5, 10]},      # Multiple return periods
    'sma': {'periods': [10, 30, 50]},        # Multiple SMA periods
    'volatility': {'periods': [10, 30]},      # Multiple volatility periods
    'rsi': {'periods': [14, 28]},            # Multiple RSI periods
    'volume': {'periods': [5, 10, 20]}       # Volume features
}

# Get list of all features that will be generated
available_features = list_available_features(feature_config)
print("\nAvailable Features:")
for feature in available_features:
    print(f"- {feature}")

# Select features to use (you can modify this list)
selected_features = [
    'return_1', 'return_5',                  # Short and medium-term returns
    'sma_ratio_10_30', 'sma_ratio_30_50',   # SMA ratios
    'volatility_10',                         # Short-term volatility
    'rsi_14',                                # Standard RSI
    'volume_ratio_5'                         # Short-term volume trend
]

print("\nSelected Features:")
for feature in selected_features:
    print(f"- {feature}")

# First train the model
print("\nTraining XGBoost model...")
train_model(
    df_path="data/BTC-Daily.csv",
    model_type=MODEL_TYPE,
    save_path=MODEL_PATH,
    features=selected_features,
    feature_config=feature_config,
    max_depth=3,
    learning_rate=0.1,
    n_estimators=100
)

# Load the trained model
print("\nLoading trained model...")
model = load_model(MODEL_TYPE, model_path=MODEL_PATH)

# Print feature importance
importance_df = model.get_feature_importance()
print("\nFeature Importance:")
print(importance_df)

# Plot feature importance
plt.figure(figsize=(10, 6))
plt.barh(importance_df['feature'], importance_df['importance'])
plt.title('Feature Importance')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('feature_importance.png')
plt.close()

print("\nRunning backtest with trained model...")
# Then run backtest with trained model
df, trades_df, performance = run_backtest(
    strategy_class=MLSignalStrategy,
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=True,
    kwargs={
        'model': model,
        'features': selected_features,
        'feature_config': feature_config
    }
)

# Print performance metrics
print("\nPerformance Metrics:")
performance.print_all()

# Visualization and trade logging
plot_equity_curve(df["equity"])
plot_drawdown(df["equity"])
plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
plot_trade_returns(trades_df)
save_trade_log(trades_df)

print("\nBacktest completed. Check the generated plots and trade log for detailed analysis.")