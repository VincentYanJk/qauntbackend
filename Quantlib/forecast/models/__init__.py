"""
Models module initialization
"""
from .base_model import BaseModel
from .xgboost_model import XGBoostModel
from .lstm_model import LSTMModel
from .random_forest_model import RandomForestModel
from .logistic_model import LogisticModel

# Registry of available models
MODEL_REGISTRY = {
    "xgboost": XGBoostModel,
    "lstm": LSTMModel,
    "random_forest": RandomForestModel,
    "logistic": LogisticModel
}

__all__ = [
    'MODEL_REGISTRY',
    'BaseModel',
    'XGBoostModel',
    'LSTMModel',
    'RandomForestModel', 
    'LogisticModel'
]