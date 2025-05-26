import backtrader as bt
import datetime

class CSVDataLoader:
    @staticmethod
    def load(filepath):
        return bt.feeds.GenericCSVData(
            dataname=filepath,
            dtformat='%Y-%m-%d %H:%M:%S',
            timeframe=bt.TimeFrame.Days,
            compression=1,
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            openinterest=-1
        )