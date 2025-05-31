"""
Unified model predictor module
"""
from .factory import load_model

class Predictor:
    """Universal predictor class for all model types"""
    
    def __init__(self, model_type, model_path=None):
        """
        Initialize predictor
        
        Args:
            model_type: Type of model ("xgboost", "lstm", etc)
            model_path: Path to saved model (default: models/{model_type}_model.{ext})
        """
        self.model = load_model(model_type, model_path)

    def predict(self, row, features=None):
        """
        Make prediction for a single row of features
        
        Args:
            row: Dict of feature values or array-like
            features: List of feature names if row is a dict
        """
        return self.model.predict(row, features=features)