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
from Quantlib.forecast.features import list_available_features, generate_features
import os
import pandas as pd
import matplotlib.pyplot as plt
import shap
import numpy as np

# Ensure models directory exists
os.makedirs("models", exist_ok=True)
os.makedirs("data/optimization_XGboost/feature-importance", exist_ok=True)

MODEL_TYPE = "xgboost"
MODEL_PATH = f"models/{MODEL_TYPE}_model.pkl"

# First train the model
print("\nTraining XGBoost model...")

# Define feature configuration
feature_config = {
    'returns': {'periods': [1, 5, 10]},      # Multiple return periods
    'sma': {'periods': [10, 30, 50]},        # Multiple SMA periods
    'volatility': {'periods': [10, 30]},      # Multiple volatility periods
    'rsi': {'periods': [14, 28]},            # Multiple RSI periods
    'volume': {'periods': [5, 10, 20]},      # Volume features
    'momentum': {'periods': [5]},            # Momentum feature
    'mfi': {
        'periods': [14],
        'overbought': 80.0,
        'oversold': 20.0
    }
}

# Get list of all features that will be generated
available_features = list_available_features(feature_config)
print("\nAvailable Features:")
for feature in available_features:
    print(f"- {feature}")

# Select features to use
selected_features = [
    'return_1', 'return_5',                  # Short and medium-term returns
    'sma_ratio_10_30', 'sma_ratio_30_50',   # SMA ratios
    'volatility_10',                         # Short-term volatility
    'rsi_14',                                # Standard RSI
    'volume_ratio_5',                        # Short-term volume trend
    'momentum_5'                             # Price momentum
]

print("\nSelected Features:")
for feature in selected_features:
    print(f"- {feature}")

print("\nTraining XGBoost models with different numbers of boosting rounds...")

for n_rounds in [50, 100, 200]:
    print(f"\nTesting with {n_rounds} boosting rounds:")
    train_model(
        df_path="data/BTC-Daily.csv",
        model_type=MODEL_TYPE,
        save_path=MODEL_PATH,
        features=selected_features,
        feature_config=feature_config,
        max_depth=3,
        learning_rate=0.1,
        n_estimators=n_rounds
    )
    print("-" * 50)

# Load the trained model
print("\nLoading trained model...")
model = load_model(MODEL_TYPE, model_path=MODEL_PATH)

# Print feature importance
importance_df = model.get_feature_importance()
print("\nFeature Importance:")
print(importance_df)

# # Plot feature importance
# plt.figure(figsize=(10, 6))
# plt.barh(importance_df['feature'], importance_df['importance'])
# plt.title('Feature Importance')
# plt.xlabel('Importance Score')
# plt.tight_layout()
# plt.savefig('data/optimization_XGboost/feature-importance/feature_importance.png')
# plt.close()

# # Prepare data for SHAP analysis
# print("\nPreparing data for SHAP analysis...")
# df = pd.read_csv("data/BTC-Daily.csv", parse_dates=["datetime"])
# df.columns = [col.strip().lower() for col in df.columns]
# df = generate_features(df, feature_config)
# X = df[selected_features].dropna()

# # Calculate SHAP values
# print("\nCalculating SHAP values...")
# explainer = shap.TreeExplainer(model.model)
# shap_values = explainer.shap_values(X)

# # Plot SHAP summary
# print("\nGenerating SHAP summary plot...")
# plt.figure(figsize=(10, 8))
# shap.summary_plot(shap_values, X, plot_type="bar", show=False)
# plt.title('SHAP Feature Importance')
# plt.tight_layout()
# plt.savefig('data/optimization_XGboost/feature-importance/shap_importance.png')
# plt.close()

# # Plot SHAP summary with feature values
# print("\nGenerating detailed SHAP summary plot...")
# plt.figure(figsize=(12, 8))
# shap.summary_plot(shap_values, X, show=False)
# plt.title('SHAP Feature Impact')
# plt.tight_layout()
# plt.savefig('data/optimization_XGboost/feature-importance/shap_impact.png')
# plt.close()

# # Generate SHAP dependence plots for top features
# print("\nGenerating SHAP dependence plots...")
# top_features = importance_df['feature'].head(3).tolist()
# for feature in top_features:
#     plt.figure(figsize=(10, 6))
#     shap.dependence_plot(feature, shap_values, X, show=False)
#     plt.title(f'SHAP Dependence Plot: {feature}')
#     plt.tight_layout()
#     plt.savefig(f'data/optimization_XGboost/feature-importance/shap_dependence_{feature}.png')
#     plt.close()

# # Calculate and print average SHAP values for each feature
# print("\nAverage absolute SHAP values per feature:")
# mean_shap = pd.DataFrame({
#     'feature': selected_features,
#     'mean_abs_shap': np.abs(shap_values).mean(0)
# })
# mean_shap = mean_shap.sort_values('mean_abs_shap', ascending=False)
# print(mean_shap)

# # Generate SHAP waterfall plot for a representative instance
# print("\nGenerating SHAP waterfall plot...")
# # Choose an interesting instance (e.g., one with high absolute SHAP values)
# total_shap = np.abs(shap_values).sum(1)
# interesting_idx = np.argmax(total_shap)
# plt.figure(figsize=(10, 6))
# shap.plots._waterfall.waterfall_legacy(explainer.expected_value, 
#                                      shap_values[interesting_idx], 
#                                      X.iloc[interesting_idx], 
#                                      show=False)
# plt.title('SHAP Waterfall Plot (Most Impactful Instance)')
# plt.tight_layout()
# plt.savefig('data/optimization_XGboost/feature-importance/shap_waterfall.png')
# plt.close()

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
        'feature_config': feature_config,
        'commission_scheme': {
            'commission': 0.002,  # 0.2% commission per trade
            'margin': False,
            'mult': 1.0
        }
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

print("\nAnalysis completed. Check the generated plots for detailed SHAP analysis.")