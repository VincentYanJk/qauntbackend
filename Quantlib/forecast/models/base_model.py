"""
Base model class that all models should inherit from
"""
from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def fit(self, X_train, y_train, **kwargs):
        """Train the model"""
        pass
        
    @abstractmethod
    def predict(self, X, **kwargs):
        """Make predictions"""
        pass
        
    @abstractmethod
    def save(self, path):
        """Save model to disk"""
        pass
        
    @abstractmethod
    def load(self, path):
        """Load model from disk"""
        pass