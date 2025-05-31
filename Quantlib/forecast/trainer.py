"""
Unified model training module
"""
import pandas as pd
import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from .features import generate_features
from .factory import create_model

def train_model(df_path, model_type="xgboost", save_path=None, features=None, **model_kwargs):
    """
    Train any supported model type with configurable features and parameters
    
    Args:
        df_path: Path to data file
        model_type: Type of model to train ("xgboost", "lstm", etc)
        save_path: Where to save the model (default: models/{model_type}_model.{ext})
        features: List of features to use (default: basic feature set)
        **model_kwargs: Additional model parameters
    """
    # Set default save path if not provided
    if save_path is None:
        ext = "pt" if model_type == "lstm" else "pkl"
        save_path = f"models/{model_type}_model.{ext}"

    # Read and preprocess data
    df = pd.read_csv(df_path, parse_dates=["datetime"])
    df = generate_features(df)
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    # Use provided features or default set
    features = features or ["return_1", "sma_ratio", "volatility"]
    X = df[features].fillna(0)
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Initialize and train model
    model = create_model(model_type, **model_kwargs)
    
    if model_type == "lstm":
        # Special handling for LSTM training
        train_lstm(model, X_train, y_train, **model_kwargs)
    else:
        # Standard training for other models
        model.fit(X_train, y_train, features=features)

    # Print performance metrics
    y_pred = model.predict(X_test, features=features)
    print(classification_report(y_test, y_pred))

    # Create directory if needed and save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)
    print(f"Model saved to {save_path}")

def train_lstm(model, X_train, y_train, batch_size=32, epochs=10, **kwargs):
    """Helper function for LSTM training"""
    X_tensor = torch.FloatTensor(X_train.values)
    y_tensor = torch.FloatTensor(y_train.values).reshape(-1, 1)
    
    dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters())
    
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