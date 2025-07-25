# SHAP-Based Model Interpretation Report (v2)

This report summarizes the updated SHAP analysis and XGBoost model interpretation after adding the `momentum_5` feature.

---

## 🎯 Model Overview

- **Model Type**: XGBoost (Binary Classification)
- **Target**: Trade vs. No Trade (1 = Trade, 0 = No Trade)

### 📊 Performance Metrics

| Class | Label     | Precision | Recall | F1-score | Support |
|-------|-----------|-----------|--------|----------|---------|
| 0     | No Trade  | 0.51      | 0.96   | 0.67     | 264     |
| 1     | Trade     | 0.56      | 0.05   | 0.10     | 257     |

> 🔍 **Observation**:
> - The model performs well in **identifying non-trade opportunities (Class 0)** but struggles significantly with **capturing actual trade signals (Class 1)**.
> - Low recall for Class 1 (0.05) indicates **many missed trades**, despite moderate precision.

---

## 🔍 Feature Importance (XGBoost Gain-based)

| Rank | Feature           | Importance Score |
|------|-------------------|------------------|
| 1    | `momentum_5`      | 0.197980 ✅
| 2    | `volatility_10`   | 0.176877
| 3    | `sma_ratio_10_30` | 0.164028
| 4    | `sma_ratio_30_50` | 0.111618
| 5    | `return_5`        | 0.095519
| 6    | `return_1`        | 0.091524
| 7    | `volume_ratio_5`  | 0.086803
| 8    | `rsi_14`          | 0.075652

> 🧠 The newly added `momentum_5` is now the **most important feature** by gain, justifying its inclusion.

---

## 📈 SHAP Interpretation Summary

### SHAP Feature Importance

- `sma_ratio_10_30` and `volatility_10` consistently appear as top impactful features.
- `momentum_5` also contributes substantially, aligning with XGBoost's gain-based importance.

### SHAP Dependence Highlights

- **`momentum_5`**: Negative momentum generally reduces the model’s confidence in trade (SHAP < 0), particularly under low volume.
- **`sma_ratio_10_30`**: Exhibits nonlinear influence; when SMA10/30 < 0.9, generally negative SHAP impact; >1.1, positive impact.
- **`volatility_10`**: Low volatility aligns with near-zero or slightly negative SHAP values, while high volatility has high positive impact (associated with trading activity).
- **`rsi_14`**: Very low impact; likely redundant or not informative in this dataset.

### SHAP Waterfall Plot Insight

- A single high-confidence “trade” prediction (SHAP total = 0.883) was driven mostly by:
  - `volatility_10` (+0.88)
  - `return_5` (+0.24)
  - `return_1` (+0.15)
- Meanwhile, `volume_ratio_5`, `momentum_5`, and `sma_ratio_10_30` reduced the score.

---

## 🧪 Feature Effectiveness Summary

| Feature           | SHAP Effective? | XGBoost Important? | Notes |
|-------------------|------------------|---------------------|-------|
| `momentum_5`      | ✅ Yes (clear signal direction) | ✅ Highest |
| `volatility_10`   | ✅ Yes | ✅ High |
| `sma_ratio_10_30` | ✅ Yes (nonlinear) | ✅ High |
| `sma_ratio_30_50` | ❌ Weak effect in SHAP | ✅ Medium |
| `return_5`        | ✅ Moderate | ✅ Medium |
| `return_1`        | ❌ Minor | ✅ Medium |
| `volume_ratio_5`  | ❌ Noisy | ✅ Low |
| `rsi_14`          | ❌ Flat impact | ✅ Low |

---

## 🛠️ Recommendations

### 🔧 Model Adjustment Suggestions

- **Fix imbalance**: Use SMOTE, undersampling, or class weights to improve recall for Class 1 (Trade).
- **Threshold tuning**: Consider lowering the prediction threshold to improve trade detection (increase recall).
- **Remove weak features**: `rsi_14`, `volume_ratio_5`, `return_1` show limited value in SHAP — consider dropping them.
- **Feature engineering**: Add lagged versions or rolling z-scores for strong features (`momentum`, `volatility`, `SMA`).

### 🔁 Pre/Post Comparison Strategy

1. Train current model → Save metrics (accuracy, F1, SHAP top 5).
2. Apply changes (e.g., drop weak features or tune threshold).
3. Retrain → Compare:
   - Precision/recall on Trade class
   - SHAP plots before/after: check if high-impact features remain stable
   - Confusion matrix delta

---

## ✅ Final Takeaway

Your model correctly learns patterns around momentum, volatility, and moving average crossovers. But it is **currently biased towards “No Trade” predictions** and **misses most true trade signals**.

The next key milestone is improving **recall for Class 1**, while maintaining model interpretability through SHAP.