import joblib
import numpy as np

class TreePredictor:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def predict(self, row):
        features = np.array([[row['return_1'], row['sma_ratio'], row['volatility']]])
        return int(self.model.predict(features)[0])