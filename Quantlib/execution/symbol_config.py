# Symbol-specific trade unit configuration for Binance
SYMBOL_CONFIG = {
    "BTCUSDT": {
        "min_qty": 0.0001,
        "step_size": 0.0001,
        "precision": 6
    },
    "ETHUSDT": {
        "min_qty": 0.001,
        "step_size": 0.001,
        "precision": 5
    },
    "BNBUSDT": {
        "min_qty": 0.01,
        "step_size": 0.01,
        "precision": 2
    },
    "SOLUSDT": {
        "min_qty": 0.1,
        "step_size": 0.1,
        "precision": 1
    },
    
    "XRPUSDT": {
        "min_qty": 1,
        "step_size": 1,
        "precision": 0
    },
    "BCHUSDT": {
        "min_qty": 0.001,
        "step_size": 0.001,
        "precision": 3
    },
    "ADAUSDT": {
        "min_qty": 1,
        "step_size": 1,
        "precision": 0
    }
}

def round_quantity(symbol, quantity):
    precision = SYMBOL_CONFIG.get(symbol, {}).get("precision", 6)
    return round(quantity, precision)