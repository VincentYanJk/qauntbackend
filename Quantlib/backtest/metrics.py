import numpy as np
import pandas as pd

class PerformanceAnalyzer:
    @staticmethod
    def compute_equity_curve(trade_history, initial_cash):
        """
        Compute equity curve from trade history
        
        Args:
            trade_history: DataFrame with columns ['datetime', 'type', 'price', 'size', 'commission']
            initial_cash: Initial capital
            
        Returns:
            DataFrame with equity curve
        """
        df = trade_history.copy()
        df['cash'] = initial_cash
        position = 0
        cash = initial_cash
        position_value = 0
        equity = []

        for i, row in df.iterrows():
            if row['type'] == 'BUY':
                cost = row['price'] * row['size'] + row['commission']
                position += row['size']
                cash -= cost
            elif row['type'] == 'SELL' and position > 0:
                proceeds = row['price'] * row['size'] - row['commission']
                position -= row['size']
                cash += proceeds
            
            # Calculate current position value
            position_value = position * row['price'] if position > 0 else 0
            # Total equity is cash plus position value
            current_equity = cash + position_value
            equity.append(current_equity)

        df['equity'] = equity
        df['position_value'] = position_value
        df['cash'] = cash
        return df

    @staticmethod
    def max_drawdown(equity_curve):
        """
        Calculate maximum drawdown and related metrics
        
        Args:
            equity_curve: Series of equity values
            
        Returns:
            float: Maximum drawdown as a percentage
        """
        if len(equity_curve) < 2:
            return 0.0
            
        # Calculate running maximum
        rolling_max = equity_curve.cummax()
        # Calculate drawdown series
        drawdown = (equity_curve - rolling_max) / rolling_max
        # Return the worst drawdown
        return drawdown.min()

    @staticmethod
    def sharpe_ratio(returns, risk_free_rate=0.02):  # Default 2% risk-free rate
        # Convert annual risk-free rate to daily
        daily_rf = (1 + risk_free_rate) ** (1/365) - 1
        excess_returns = returns - daily_rf
        
        # Calculate annualized Sharpe ratio using 365 days for crypto
        ann_return = (1 + returns.mean()) ** 365 - 1
        ann_vol = returns.std() * np.sqrt(365)
        
        return (ann_return - risk_free_rate) / ann_vol if ann_vol != 0 else 0

    @staticmethod
    def analyze(trade_df, initial_cash):
        """
        Perform comprehensive analysis of trading results
        
        Args:
            trade_df: DataFrame with trade history
            initial_cash: Initial capital
            
        Returns:
            dict with comprehensive performance metrics
        """
        # Compute equity curve with position tracking
        equity_df = PerformanceAnalyzer.compute_equity_curve(trade_df, initial_cash)
        equity = equity_df['equity']
        
        # Calculate returns
        returns = equity.pct_change().dropna()
        
        # Get trade statistics
        trade_stats = PerformanceAnalyzer.win_rate(trade_df)
        
        # Calculate drawdown metrics
        max_dd = PerformanceAnalyzer.max_drawdown(equity)
        
        # Calculate Sharpe ratio
        sharpe = PerformanceAnalyzer.sharpe_ratio(returns)
        
        # Calculate additional metrics
        total_return = (equity.iloc[-1] - initial_cash) / initial_cash
        total_trades = len(trade_df)
        total_commission = trade_df['commission'].sum() if 'commission' in trade_df.columns else 0
        
        result = {
            'initial_capital': initial_cash,
            'final_capital': equity.iloc[-1],
            'total_return': total_return,
            'total_trades': total_trades,
            'total_commission': total_commission,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'win_rate': trade_stats['win_rate'],
            'profit_factor': trade_stats['profit_factor'],
            'avg_win': trade_stats['avg_win'],
            'avg_loss': trade_stats['avg_loss'],
            'largest_win': trade_stats['largest_win'],
            'largest_loss': trade_stats['largest_loss'],
            'equity_curve': equity,
            'returns': returns
        }
        return result

    @staticmethod
    def win_rate(df):
        """
        Calculate win rate and related metrics
        
        Args:
            df: DataFrame with trade history including ['pnl', 'pnlcomm', 'commission']
            
        Returns:
            dict with trade metrics:
            - win_rate: Percentage of winning trades
            - profit_factor: Gross profit / Gross loss
            - avg_win: Average winning trade
            - avg_loss: Average losing trade
            - largest_win: Largest winning trade
            - largest_loss: Largest losing trade
        """
        if len(df) == 0:
            return {
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0
            }
            
        # Use pnlcomm (PnL after commission) to determine winners/losers
        winners = df[df['pnlcomm'] > 0]
        losers = df[df['pnlcomm'] < 0]
        
        n_winners = len(winners)
        n_losers = len(losers)
        total_trades = n_winners + n_losers
        
        if total_trades == 0:
            return {
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0
            }
            
        win_rate = n_winners / total_trades
        
        # Calculate profit metrics
        gross_profit = winners['pnlcomm'].sum() if n_winners > 0 else 0
        gross_loss = abs(losers['pnlcomm'].sum()) if n_losers > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')
        
        # Calculate trade size metrics
        avg_win = winners['pnlcomm'].mean() if n_winners > 0 else 0
        avg_loss = losers['pnlcomm'].mean() if n_losers > 0 else 0
        largest_win = winners['pnlcomm'].max() if n_winners > 0 else 0
        largest_loss = losers['pnlcomm'].min() if n_losers > 0 else 0
        
        return {
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss
        }