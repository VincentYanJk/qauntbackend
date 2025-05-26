from Quantlib.forecast.predictor.tree_predictor import TreePredictor
from Quantlib.forecast.predictor.deep_predictor import LSTMPredictor

def load_model(model_type):
    if model_type == "xgboost":
        return TreePredictor("models/xgb_model.pkl")
    elif model_type == "lstm":
        return LSTMPredictor("models/lstm_model.pt")
    else:
        raise ValueError(f"Unknown model type: {model_type}")