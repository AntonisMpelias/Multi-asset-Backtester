import pandas as pd
import numpy as np
import yaml

with open("config/backtest.yaml", "r") as f:
    backtest_info = yaml.safe_load(f)

drawdown_limit = backtest_info['drawdown_limit']

class killswitch:
    def on_start(self,df):
        self.df= df
        self.dd_limit = drawdown_limit
        #Doing some important computations to decide if using the killswitch is needed later on
        self.temp_returns = self.df['Returns'] * self.df['Signal'].shift(1)
        self.temp_portfolio = (1 + self.temp_returns.fillna(0)).cumprod()
        self.temp_dd = self.temp_portfolio / self.temp_portfolio.cummax() -1

        #If the three following variables are all true, then the killswitch activates
        self.high_vol = self.df['Volatility_shift'] > self.df['Vol_Threshold_shift']
        self.downtrend = self.df['Momentum_shift'] < 0
        self.dd_breach = self.temp_dd.shift(1) < self.dd_limit

        return self.dd_breach & self.high_vol & self.downtrend
