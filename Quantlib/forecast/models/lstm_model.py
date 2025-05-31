import torch
import torch.nn as nn
import numpy as np
from .base_model import BaseModel

class LSTMNetwork(nn.Module):
    def __init__(self, input_size=3, hidden_size=32, output_size=1):
        super(LSTMNetwork, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = x.unsqueeze(1) if len(x.shape) == 2 else x
        _, (hn, _) = self.lstm(x)
        out = self.fc(hn[-1])
        return self.sigmoid(out)

class LSTMModel(BaseModel):
    def __init__(self, input_size=3, hidden_size=32, **kwargs):
        self.params = {
            'input_size': input_size,
            'hidden_size': hidden_size,
            **kwargs
        }
        self.model = LSTMNetwork(input_size=input_size, hidden_size=hidden_size)
        self.criterion = nn.BCELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters())
        
    def fit(self, X_train, y_train, **kwargs):
        X_tensor = torch.FloatTensor(X_train.values)
        y_tensor = torch.FloatTensor(y_train.values).reshape(-1, 1)
        
        self.model.train()
        for epoch in range(kwargs.get('epochs', 10)):
            self.optimizer.zero_grad()
            output = self.model(X_tensor)
            loss = self.criterion(output, y_tensor)
            loss.backward()
            self.optimizer.step()
        return self
        
    def predict(self, X, **kwargs):
        self.model.eval()
        if isinstance(X, dict):
            features = kwargs.get('features', ['return_1', 'sma_ratio', 'volatility'])
            X = np.array([[X[f] for f in features]])
        X_tensor = torch.FloatTensor(X)
        with torch.no_grad():
            output = self.model(X_tensor)
        return (output.numpy() > 0.5).astype(int).reshape(-1)
        
    def save(self, path):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'params': self.params
        }, path)
        
    def load(self, path):
        checkpoint = torch.load(path)
        self.params = checkpoint['params']
        self.model = LSTMNetwork(
            input_size=self.params['input_size'],
            hidden_size=self.params['hidden_size']
        )
        self.model.load_state_dict(checkpoint['model_state_dict'])
        return self