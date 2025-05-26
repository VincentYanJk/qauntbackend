import torch
import pandas as pd
import numpy as np
from torch.utils.data import Dataset, DataLoader
from Quantlib.forecast.models.lstm_model import LSTMModel
from Quantlib.forecast.features import generate_features
import torch.nn as nn
import torch.optim as optim
import os

class TimeSeriesDataset(Dataset):
    def __init__(self, data, seq_len=10):
        self.X, self.y = [], []
        for i in range(len(data) - seq_len):
            seq_x = data.iloc[i:i+seq_len][['return_1', 'sma_ratio', 'volatility']].values
            label = int(data.iloc[i+seq_len]['close'] > data.iloc[i+seq_len-1]['close'])
            self.X.append(seq_x)
            self.y.append(label)
        self.X = torch.tensor(self.X, dtype=torch.float32)
        self.y = torch.tensor(self.y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

def train_lstm_model(csv_path, save_path="models/lstm_model.pt", seq_len=10, epochs=10):
    df = pd.read_csv(csv_path, parse_dates=['datetime'])
    df = generate_features(df)
    dataset = TimeSeriesDataset(df, seq_len=seq_len)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = LSTMModel(input_size=3, hidden_size=32, output_size=2)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for X_batch, y_batch in dataloader:
            optimizer.zero_grad()
            output = model(X_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss:.4f}")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"Model saved to {save_path}")