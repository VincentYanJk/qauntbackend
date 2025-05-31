"""
Model factory module for creating and loading models
"""
from .models import MODEL_REGISTRY

def create_model(model_type="xgboost", **kwargs):
    """
    Factory function to create a new model instance
    """
    if model_type not in MODEL_REGISTRY:
        raise ValueError(f"Unsupported model type: {model_type}. Available models: {list(MODEL_REGISTRY.keys())}")
    
    return MODEL_REGISTRY[model_type](**kwargs)

def load_model(model_type, model_path=None):
    """
    Load a trained model from disk
    """
    if model_path is None:
        model_path = f"models/{model_type}_model.{'pt' if model_type == 'lstm' else 'pkl'}"
        
    model = create_model(model_type)
    return model.load(model_path)