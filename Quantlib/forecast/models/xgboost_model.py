import xgboost as xgb
import numpy as np
import joblib
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from .base_model import BaseModel

class XGBoostModel(BaseModel):
    def __init__(self, **kwargs):
        self.params = {
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'random_state': 42,
            'max_depth': kwargs.get('max_depth', 3),
            'learning_rate': kwargs.get('learning_rate', 0.1),
            'n_estimators': kwargs.get('n_estimators', 100),
            **kwargs
        }
        self.model = None
        self.feature_names = None
        
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> 'XGBoostModel':
        """
        Train the XGBoost model
        
        Args:
            X_train: Training features
            y_train: Training labels
            **kwargs: Additional parameters
        """
        self.feature_names = list(X_train.columns)
        dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=self.feature_names)
        self.model = xgb.train(self.params, dtrain)
        return self
        
    def predict(self, X: pd.DataFrame, **kwargs) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features for prediction
            **kwargs: Additional parameters
        
        Returns:
            Binary predictions (0 or 1)
        """
        if isinstance(X, dict):
            # Handle single feature dict
            X = pd.DataFrame([X])
        
        if isinstance(X, pd.DataFrame):
            # Ensure all required features are present
            missing_features = set(self.feature_names) - set(X.columns)
            if missing_features:
                raise ValueError(f"Missing features: {missing_features}")
            X = X[self.feature_names]  # Ensure correct feature order
        
        dtest = xgb.DMatrix(X, feature_names=self.feature_names)
        return (self.model.predict(dtest) > 0.5).astype(int)
    
    def predict_proba(self, X: pd.DataFrame, **kwargs) -> np.ndarray:
        """Get probability predictions"""
        if isinstance(X, dict):
            X = pd.DataFrame([X])
        if isinstance(X, pd.DataFrame):
            X = X[self.feature_names]
        dtest = xgb.DMatrix(X, feature_names=self.feature_names)
        return self.model.predict(dtest)
        
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance scores
        
        Returns:
            DataFrame with feature names and their importance scores
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
            
        importance_scores = self.model.get_score(importance_type='gain')
        importance_df = pd.DataFrame({
            'feature': list(importance_scores.keys()),
            'importance': list(importance_scores.values())
        })
        importance_df = importance_df.sort_values('importance', ascending=False)
        importance_df['importance'] = importance_df['importance'] / importance_df['importance'].sum()
        return importance_df
        
    def save(self, path: str):
        """Save model and feature names"""
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'params': self.params
        }
        joblib.dump(model_data, path)
        
    def load(self, path: str) -> 'XGBoostModel':
        """Load model and feature names"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.params = model_data['params']
        return self