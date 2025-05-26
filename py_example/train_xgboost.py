from Quantlib.forecast.trainer.trainer import train_model

train_model(
    df_path="data/BTCUSDT.csv",
    model_type="xgboost",
    save_path="models/xgb_model.pkl"
)