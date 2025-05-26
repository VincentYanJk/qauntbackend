import time
import pandas as pd
from binance import ThreadedWebsocketManager
from Quantlib.execution.binance_broker import BinanceBroker
from Quantlib.execution.trade_executor import LiveExecutor
from Quantlib.forecast.predictor.tree_predictor import TreePredictor
from Quantlib.execution.live_ml_strategy import LiveMLStrategy

def run_live(api_key, api_secret, model_path, symbol="BTCUSDT", features=["sma_ratio", "volatility"], qty=0.001, interval=60, use_websocket=False):
    broker = BinanceBroker(api_key, api_secret, use_futures=True)
    executor = LiveExecutor(broker, default_symbol=symbol)
    model = TreePredictor(model_path)

    strategy = LiveMLStrategy(
        executor=executor,
        model=model,
        symbol=symbol,
        qty=qty,
        features=features
    )

    print("🚀 Live trading started on symbol:", symbol)
    if use_websocket:
        def handle_socket(msg):
            try:
                k = msg['k']
                data_row = {
                    "datetime": k["t"],
                    "close": float(k["c"]),
                    # Simulated feature values (replace with actual feature calc)
                    "sma_ratio": 1.01,
                    "volatility": 0.015
                }
                strategy.on_new_tick(data_row)
            except Exception as e:
                print("⚠️ WebSocket error:", e)

        twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
        twm.start()
        twm.start_kline_socket(callback=handle_socket, symbol=symbol.lower(), interval='1m')
        while True:
            time.sleep(1)

    else:
        while True:
            try:
                df = pd.read_csv("data/BTCUSDT.csv")
                latest_row = df.iloc[-1].to_dict()
                strategy.on_new_tick(latest_row)
            except Exception as e:
                print("⚠️ Polling error:", e)
            time.sleep(interval)