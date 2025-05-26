from Quantlib.forecast.features import generate_features
from Quantlib.forecast.models.xgboost_model import create_xgboost_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import pandas as pd

def train_model(df_path, model_type="xgboost", save_path="model.pkl"):
    df = pd.read_csv(df_path, parse_dates=["datetime"])
    df = generate_features(df)
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    X = df[["return_1", "sma_ratio", "volatility"]]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    if model_type == "xgboost":
        model = create_xgboost_model()
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    joblib.dump(model, save_path)
    print(f"Model saved to {save_path}")