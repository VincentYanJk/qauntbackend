from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression

def get_model(model_type="xgboost"):
    if model_type == "xgboost":
        return XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    elif model_type == "rf":
        return RandomForestClassifier()
    elif model_type == "logistic":
        return LogisticRegression()
    else:
        raise ValueError(f"Unsupported model type: {model_type}")