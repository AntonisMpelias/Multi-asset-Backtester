import numpy as np
import pandas as pd
import yaml

#Reading the backtest info from the config so that we can get the total investment amount
with open("config/backtest.yaml", "r") as f:
    backtest_info = yaml.safe_load(f)

#Reading the asset list from the config
with open ("config/assets.yaml", "r") as f:
    asset_list= yaml.safe_load(f)

#Counting how many assets we are working with to know how to distribute the total investment 
tickers = asset_list['asset_list']
x = len(tickers)

class weight_assignment: 
    def __init__(self, dfs, investment_amount=None, total_assets=None):
        # These are evaluated EVERY time the method is called
        if investment_amount is None:
            investment_amount = backtest_info['initial_investment']  # Fresh lookup!
        if total_assets is None:
            total_assets = x  # Fresh lookup!
        
        # Deep copy to avoid modifying original DataFrames
        self.dfs = {asset_ticker: asset_df.copy() for asset_ticker, asset_df in dfs.items()}
        self.investment = investment_amount
        self.total_assets = total_assets
        
    def weighing_assets(self):
        inv_vols = {} #Initializing an empty dictionary where we will store inverse volatility(As a series) for each asset
        for ticker, df in self.dfs.items():
            inv_vols[ticker] = 1.0/(df['Volatility_shift']+ 1e-8) #saving the inverse volatility into the dict we made.
            inv_vols[ticker] = inv_vols[ticker] * (1 + ((df['SMA_7_shift']-df['SMA_30_shift'])/df['SMA_30_shift']).clip(lower=0))

        #Turning it into a dataframe
        inv_vol_df = pd.DataFrame(inv_vols) 
         #We sum the inverse-vol for each row to normalize the weights
        row_sums = inv_vol_df.sum(axis=1)
        #We replace 0s with NaNs so that we don't divide by zero
        row_sums_safe = row_sums.replace(0, np.nan)
        #We now have to normalize the weights so that we don't leave cash on the table. Otherwise on periods where all assets have volatile periods we could leave majority of our investment sitting doing nothing
        normalized_weights_df = inv_vol_df.div(row_sums_safe, axis=0)
        for ticker, df in self.dfs.items():
            # reindex to the df's index in case indexes differ; this aligns dates safely
            df['Weight'] = normalized_weights_df[ticker].reindex(df.index)
            #Filling NaNs as zeros only after we did the calculations, because early NaNs are legitimate missing values that shouldn't be treated as zeros
            df['Weight'] = df['Weight'].fillna(0)

        return self.dfs
