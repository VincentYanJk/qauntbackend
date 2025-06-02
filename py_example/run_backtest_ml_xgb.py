from Quantlib.visualization.visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_signals,
    save_trade_log
)

from Quantlib.strategies.ml_signal_strategy import MLSignalStrategy
from Quantlib.backtest.engine import run_backtest
from Quantlib.forecast import load_model, train_model
import os

# Ensure models directory exists
os.makedirs("models", exist_ok=True)

MODEL_TYPE = "xgboost"
MODEL_PATH = f"models/{MODEL_TYPE}_model.pkl"
FEATURES = ["return_1", "sma_ratio", "volatility"]  # Match the default feature set

# First train the model
print("Training XGBoost model...")
train_model(
    df_path="data/BTC-Daily.csv",
    model_type=MODEL_TYPE,
    save_path=MODEL_PATH,
    features=FEATURES  # Specify the features to use
)

# Load the trained model
print("Loading trained model...")
model = load_model(MODEL_TYPE, model_path=MODEL_PATH)

print("Running backtest with trained model...")
# Then run backtest with trained model
df, trades_df, performance = run_backtest(
    strategy_class=MLSignalStrategy,
    data_path="data/BTC-Daily.csv",
    cash=100000,
    plot=True,
    kwargs={
        'model': model,  # Pass the model instance directly
        'features': FEATURES  # Use the same features as training
    }
)

# Print performance metrics
performance.print_all()

# Visualization and trade logging
plot_equity_curve(df["equity"])
plot_drawdown(df["equity"])
plot_signals(df, df.get("buy_signal"), df.get("sell_signal"))
save_trade_log(trades_df)