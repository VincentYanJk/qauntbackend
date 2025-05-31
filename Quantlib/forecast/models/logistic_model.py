from sklearn.linear_model import LogisticRegression
import joblib
import numpy as np
from .base_model import BaseModel

class LogisticModel(BaseModel):
    def __init__(self, **kwargs):
        self.params = {
            'random_state': 42,
            **kwargs
        }
        self.model = LogisticRegression(**self.params)
        
    def fit(self, X_train, y_train, **kwargs):
        self.model.fit(X_train, y_train)
        return self
        
    def predict(self, X, **kwargs):
        if isinstance(X, dict):
            X = np.array([[X[f] for f in kwargs.get('features', ['return_1', 'sma_ratio', 'volatility'])]])
        return self.model.predict(X)
        
    def save(self, path):
        joblib.dump(self.model, path)
        
    def load(self, path):
        self.model = joblib.load(path)
        return self