import numpy as np
import pandas as pd

class Hybrid_strat:
    #Initializing the empty dataframe
    def __init__(self):
        self.df= None     #We will store the dataframe here
   
    def on_start(self, df):
        self.df = df

        #Calculating indicators for the final signal
        self.df['SMA 30'] = self.df['Close'].rolling(window=30).mean() # 30 day moving average
        self.df['SMA 7'] = self.df['Close'].rolling(window=7).mean() # 7 day moving average
        self.df['Momentum'] = self.df['Close'] - self.df["Close"].shift(30) #Momentum indicator. Positive= Uphill trend, Negative= Downhill trend
        self.df['Volatility'] = self.df['Returns'].rolling(window=30).std() # Volatility, what else do I explain smh.
        self.df['Z-score'] = (self.df['Close'] - self.df['Close'].rolling(window=30).mean()) / self.df['Close'].rolling(window=30).std() # Z-score = How many standard deviations are we from the mean
        self.df['Vol_Threshold'] = self.df['Volatility'].rolling(window=30).median() #Volatility threshold to have a base. Used median instead of mean for more stable results

        #Shifting Volatility/Volatility Threshold and Momentum to avoid soft look-ahead bias
        self.df['Volatility_shift'] = self.df['Volatility'].shift(1)
        self.df['Vol_Threshold_shift'] = self.df['Vol_Threshold'].shift(1)
        self.df['Momentum_shift'] = self.df['Momentum'].shift(1)
        self.df['SMA_30_shift'] = self.df['SMA 30'].shift(1)
        self.df['SMA_7_shift']  = self.df['SMA 7'].shift(1)
        self.df['Z-score_shift'] = self.df['Z-score'].shift(1)


        #Initializing signals
        self.df['SMA_signal'] = np.where(self.df['SMA_7_shift']> self.df['SMA_30_shift'], 1, 0)
        self.df['MR_signal'] = np.where(self.df['Z-score_shift'] < -1.5, 1, np.where(self.df['Z-score_shift'] > 1.5, -1, 0))

        #Hybrid switching logic 
        conditions = [
            (self.df['Volatility_shift'] <= self.df['Vol_Threshold_shift']) , #Low/Normal Vol -> SMA
            (self.df['Volatility_shift'] >= self.df['Vol_Threshold_shift']) & (self.df['Momentum_shift'] > 0), #High Vol but positive Momentum -> Still SMA
            (self.df['Volatility_shift'] >=self.df['Vol_Threshold_shift']) & (self.df['Momentum_shift'] <= 0) #High Vol AND negative Momentum -> MR

        ]

        choices = [
            self.df['SMA_signal'] , 
            self.df['SMA_signal'],
            self.df['MR_signal']
        ]

        self.df['Signal'] = np.select(conditions, choices, default = 0)
   
        return self.df
