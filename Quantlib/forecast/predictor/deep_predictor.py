import torch
import numpy as np
from Quantlib.forecast.models.lstm_model import LSTMModel

class LSTMPredictor:
    def __init__(self, model_path):
        self.model = LSTMModel(input_size=3, hidden_size=32, output_size=2)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def predict(self, row):
        features = torch.tensor([[row['return_1'], row['sma_ratio'], row['volatility']]], dtype=torch.float32)
        output = self.model(features)
        return int(torch.argmax(output, dim=1).item())