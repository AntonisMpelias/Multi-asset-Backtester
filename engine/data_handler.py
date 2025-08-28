import yfinance as yf
import pandas as pd 
import numpy as np 
import yaml 
import os

#Reading the asset list from the config
with open("config/assets.yaml", "r") as f:
    asset_list = yaml.safe_load(f)

#Reading the backtest info from the config so that we can get the starting and ending date
with open("config/backtest.yaml", "r") as f:
    backtest_info = yaml.safe_load(f)

class data_handler:
    def __init__(self, asset_list=None, start_date=None, end_date=None):
        # ADDED these 6 lines:
        if asset_list is None:
            asset_list = globals()['asset_list']['asset_list']
        if start_date is None:
            start_date = globals()['backtest_info']['start_date'] 
        if end_date is None:
            end_date = globals()['backtest_info']['end_date']
        self.dfs = {}
        self.asset_list = asset_list
        self.start_date = start_date
        self.end_date = end_date

    def data_fetching(self):
        #Looping through all assets to save each individual dataframe or read it if we have already saved it
        for company_name, ticker in self.asset_list.items():
            #Saving the path of the raw and processed files
            raw_path = f"data/raw/{ticker}_{self.start_date}_{self.end_date}.csv"
            processed_path = f"data/processed/{ticker}_{self.start_date}_{self.end_date}.csv"

            #If processed CSV exists, read it
            if os.path.exists(processed_path):
                self.dfs[ticker] = pd.read_csv(processed_path, index_col=0, parse_dates=True, skiprows=[1,2])

            else:
                #If it doesn't exist we download it and save it on a CSV
                self.dfs[ticker] = yf.download(ticker, start=self.start_date, end=self.end_date)
                if self.dfs[ticker].empty:
                    raise ValueError(f"No data for {ticker}")
                else:
                    # Save raw CSV for backup
                    os.makedirs("data/raw", exist_ok=True)
                    self.dfs[ticker].to_csv(raw_path)

                #Adding a returns column to the dataframe and dropping NaNs. 
                self.dfs[ticker]['Returns'] = self.dfs[ticker]['Close'].pct_change()
                self.dfs[ticker] = self.dfs[ticker].dropna()

                #Saving the dataframe as a processed CSV
                os.makedirs("data/processed", exist_ok=True)
                self.dfs[ticker].to_csv(processed_path)
            
        return self.dfs
    def SPY_fetching_for_plotting(self): #We will compare the results to the S&P 500, the process is almost identical as the previous function
        raw_path = f"data/raw/SPY_{self.start_date}_{self.end_date}.csv"
        processed_path = f"data/processed/SPY_{self.start_date}_{self.end_date}.csv"

        #Cheking if we have already downloaded the S&P 500 in this timeperiod before
        if os.path.exists(processed_path):
            SPY_df = pd.read_csv(processed_path, index_col=0, parse_dates= True, skiprows=[1,2])
        else:
            SPY_df = yf.download('SPY', start= self.start_date, end= self.end_date)
            
            # Save raw CSV for backup
            os.makedirs("data/raw", exist_ok=True)
            SPY_df.to_csv(raw_path)
            
            #Adding a returns column to the dataframe and dropping NaNs.
            SPY_df['Returns'] = SPY_df['Close'].pct_change() 
            SPY_df = SPY_df.dropna()
            
            #Saving the dataframe as a processed CSV
            os.makedirs("data/processed", exist_ok=True)
            SPY_df.to_csv(processed_path)
        
        return SPY_df
