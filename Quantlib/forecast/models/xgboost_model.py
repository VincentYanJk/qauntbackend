import xgboost as xgb
import numpy as np
import joblib
from .base_model import BaseModel

class XGBoostModel(BaseModel):
    def __init__(self, **kwargs):
        self.params = {
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'random_state': 42,
            **kwargs
        }
        self.model = None
        
    def fit(self, X_train, y_train, **kwargs):
        dtrain = xgb.DMatrix(X_train, label=y_train)
        self.model = xgb.train(self.params, dtrain)
        return self
        
    def predict(self, X, **kwargs):
        if isinstance(X, dict):
            # Handle single feature dict
            X = np.array([[X[f] for f in kwargs.get('features', ['return_1', 'sma_ratio', 'volatility'])]])
        dtest = xgb.DMatrix(X)
        return (self.model.predict(dtest) > 0.5).astype(int)
        
    def save(self, path):
        joblib.dump(self.model, path)
        
    def load(self, path):
        self.model = joblib.load(path)
        return self