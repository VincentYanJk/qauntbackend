import xgboost as xgb
import numpy as np

class XGBoostModel:
    def __init__(self, input_dim=3, output_dim=2, params=None):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.params = params or {
            'objective': 'multi:softprob',
            'num_class': output_dim,
            'eval_metric': 'mlogloss'
        }
        self.model = None

    def fit(self, X_train, y_train):
        dtrain = xgb.DMatrix(np.array(X_train), label=np.array(y_train))
        self.model = xgb.train(self.params, dtrain)

    def predict(self, X):
        dtest = xgb.DMatrix(np.array(X))
        probas = self.model.predict(dtest)
        return np.argmax(probas, axis=1)