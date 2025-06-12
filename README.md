# GPTQuant: BTC Quant Trading Framework

GPTQuant is a professional-grade modular framework for backtesting and live trading of Bitcoin strategies. It supports classical strategies, machine learning models, and real-time Binance integration.

---

## 📦 Project Structure

```
├── setup.py
├── README.md
├── requirements.txt
├── .vscode/
│   └── launch.json
├── Quantlib/
│   ├── __init__.py
│   ├── backtest/
│   │   ├── engine.py
│   │   ├── metrics.py
│   │   └── ...
│   ├── strategies/
│   │   ├── sma_crossover.py
│   │   ├── rsi_reversion.py
│   │   └── ...
│   ├── indicators/
│   │   ├── sma.py
│   │   ├── macd.py
│   │   └── ...
│   └── ...
├── py_example/
│   ├── run_backtest_sma.py
│   ├── Train_XGBoost_and_Backtest.py
│   └── ...
├── notebook_example/
│   ├── 01_train_xgboost.ipynb
│   └── ...
├── data/
│   └── BTCUSDT.csv

```

---

## ✅ Installation (Recommended)

Make sure you are using Python >= 3.8. Then run:

```bash
cd gptquant_project

# Install dependencies
pip install -r requirements.txt

# Install project as editable module
pip install -e .
```

---

## 🧪 Run Examples

### Run a backtest:
```bash
python py_example/run_backtest_sma.py
```

### Train & backtest with ML:
```bash
python py_example/Train_XGBoost_and_Backtest.py
```

### Explore in notebooks:
Open any notebook in `notebook_example/` with Jupyter.

---

## 📡 Live Trading

To switch from backtest to live execution:

```python
from Quantlib.execution import TradeExecutor
executor = TradeExecutor(mode="live", broker="binance")
```

---

## 🧠 Troubleshooting

- If you get `ModuleNotFoundError`, run `pip install -e .`
- In VS Code, use `.vscode/launch.json` to ensure cwd is set to project root

---
Set proxy for local to check in code when connecting VPN
git config --global http.proxy 'http://127.0.0.1:7890'
git config --global https.proxy 'http://127.0.0.1:7890'

unset:
git config --global --unset http.proxy
git config --global --unset https.proxy

MIT License • Developed by GPT + BTC Strategists