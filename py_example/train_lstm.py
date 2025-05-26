from Quantlib.forecast.trainer.deep_trainer import train_lstm_model

train_lstm_model(
    csv_path="data/BTCUSDT.csv",
    save_path="models/lstm_model.pt",
    seq_len=10,
    epochs=5
)