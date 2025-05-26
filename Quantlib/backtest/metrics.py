import numpy as np
import pandas as pd

class PerformanceAnalyzer:
    @staticmethod
    def compute_equity_curve(trade_history, initial_cash):
        df = trade_history.copy()
        df['cash'] = initial_cash
        position = 0
        cash = initial_cash
        equity = []

        for i, row in df.iterrows():
            if row['type'] == 'BUY':
                position += 1
                cash -= row['price']
            elif row['type'] == 'SELL' and position > 0:
                position -= 1
                cash += row['price']
            equity.append(cash)

        df['equity'] = equity
        return df

    @staticmethod
    def max_drawdown(equity_curve):
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        return drawdown.min()

    @staticmethod
    def sharpe_ratio(returns, risk_free_rate=0.0):
        excess_return = returns - risk_free_rate
        return np.mean(excess_return) / np.std(excess_return) * np.sqrt(252)

    @staticmethod
    def analyze(trade_df, initial_cash):
        equity_df = PerformanceAnalyzer.compute_equity_curve(trade_df, initial_cash)
        equity = equity_df['equity']
        returns = equity.pct_change().dropna()

        result = {
            'final_cash': equity.iloc[-1],
            'max_drawdown': PerformanceAnalyzer.max_drawdown(equity),
            'sharpe_ratio': PerformanceAnalyzer.sharpe_ratio(returns),
            'num_trades': len(trade_df),
            'win_rate': PerformanceAnalyzer.win_rate(trade_df),
        }
        return result

    @staticmethod
    def win_rate(df):
        wins = 0
        losses = 0
        prices = df['price'].tolist()
        types = df['type'].tolist()
        for i in range(1, len(prices), 2):
            if types[i-1] == 'BUY' and types[i] == 'SELL':
                if prices[i] > prices[i-1]:
                    wins += 1
                else:
                    losses += 1
        total = wins + losses
        return wins / total if total > 0 else 0.0