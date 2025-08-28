import pandas as pd
import numpy as np
import yaml


#Reading the asset list from the config
with open("config/assets.yaml", "r") as f:
    asset_list_config = yaml.safe_load(f)

#Reading the backtest info from the config so that we can get important data to run the backtest
with open("config/backtest.yaml", "r") as f:
    backtest_info = yaml.safe_load(f)



class performance_metrics:
    def __init__(self, dfs, asset_list=None, investment = None, slippage = None, fees = None, max_position = None, risk_per_trade= None):
        #"Refreshing" the value of the variables every time so that we avoid reusing old data that has been changed
        if asset_list is None:
            asset_list = asset_list_config['asset_list']
            self.asset_list = asset_list
        
        if investment is None:
            investment = backtest_info['initial_investment']
            self.investment = investment
        
        if slippage is None:
            slippage = backtest_info['slippage']
            self.slippage = slippage
        
        if fees is None:
            fees = backtest_info['fees']
            self.fees = fees
        
        if max_position is None:
            max_position = backtest_info['max_position']
            self.max_position = max_position
        
        if risk_per_trade is None:
            risk_per_trade = backtest_info['risk_per_trade']
            self.risk_per_trade = risk_per_trade
        
        self.dfs = dfs
        self.eps = 1e-8
    
    def calculating_performance(self):
        for company, ticker in self.asset_list.items():
            
            #Volatility based position sizing using yesterday's volatility to avoid lookahead bias
            self.dfs[ticker]['Position_Size'] = self.dfs[ticker]['Weight'] #Used position size to match my old code. The usage will be fundamentally as using the weight column instead
           
            #Aligning positions and signals so that they always use yesterday's info
            prev_pos = self.dfs[ticker]['Position_Size'].shift(1).fillna(0) #Yesterday's position
            prev_sig = self.dfs[ticker]['Signal'].shift(1).fillna(0) #Yesterday's signal

            actual_position_prev = prev_pos * prev_sig
            actual_position_current = self.dfs[ticker]['Signal']*self.dfs[ticker]['Position_Size']

            #Calculating cash B-)
            trade_returns = self.dfs[ticker]['Returns'] * actual_position_prev

            #Counting total costs based on the difference from yesterday's position to today's
            position_change = (actual_position_current - actual_position_prev).fillna(0).abs()
            cost = (self.slippage + self.fees) * position_change

            #Net returns and portfolio curve
            self.dfs[ticker]['Returns_strategy'] = trade_returns - cost
            self.dfs[ticker]['Returns_strategy'] = self.dfs[ticker]['Returns_strategy'].fillna(0)

        #Building a dict of per-asset returns (in the form of percentages for now)
        rs = {}
        for ticker in self.asset_list.values():
            rs[ticker]= self.dfs[ticker]['Returns_strategy']
        
        #Creating a dataframe from the per-asset returns 
        rs_df = pd.DataFrame(rs)

        #Aligning indexes and doing some cleanups 
        rs_df = rs_df.sort_index()
        rs_df = rs_df.fillna(0)

        # Daily portfolio fractional return = sum across assets (these are already weight*signal adjusted)
        daily_portfolio_return = rs_df.sum(axis=1)
        daily_portfolio_return = daily_portfolio_return.fillna(0)

        #Portfolio curve
        portfolio_value = float(self.investment) * (1+daily_portfolio_return).cumprod()

        #Building a small df to help with calculating the metrics
        port_df = pd.DataFrame({"Returns_strategy":daily_portfolio_return, "Portfolio_value":portfolio_value})
        port_df["Drawdown"] = port_df['Portfolio_value']/port_df['Portfolio_value'].cummax() -1

        #Computing aggregated portfolio metrics
        max_drawdown = port_df['Drawdown'].min()

        annualized_return = port_df["Returns_strategy"].mean() * 252
        annualized_vol = port_df["Returns_strategy"].std() * (252 ** 0.5)

        # Sharpe ratio (using eps to avoid div by zero)
        if annualized_vol != 0:
            sharpe_ratio = annualized_return / (annualized_vol + self.eps)
        else:
            sharpe_ratio = np.nan
        
        #Downside volatility calculations for Sortino ratio 
        downside_returns = port_df["Returns_strategy"][port_df["Returns_strategy"] < 0]
        if len(downside_returns) > 0:
            downside_vol = (np.mean(downside_returns ** 2) * 252) ** 0.5
        else:
            downside_vol = 0
        
        #Sortino
        if downside_vol > 0:
            sortino_ratio = annualized_return / (downside_vol + self.eps)
        else:
            sortino_ratio = np.nan

        initial_value = float(self.investment)
        final_value = port_df["Portfolio_value"].iloc[-1]
        total_return = (final_value / initial_value - 1) * 100

        # Win/loss on portfolio-level fractional returns, plus the winrate and lossrate
        wins = port_df["Returns_strategy"][port_df["Returns_strategy"] > 0]
        losses = port_df["Returns_strategy"][port_df["Returns_strategy"] < 0]

        total_trades = len(wins) + len(losses)
        if total_trades > 0:
            winrate = len(wins) / total_trades
            lossrate = len(losses) / total_trades
        else:
            winrate = np.nan 
            lossrate = np.nan


        #Calculating the gains from the average winning trade and the losses from the average losing trade
        if len(wins) > 0:
            avg_win = wins.mean()
        else:
            avg_win = 0

        if len(losses) > 0:
            avg_loss = losses.mean()
        else:
            avg_loss = 0

        #Calculating the calmar ratio
        if max_drawdown < 0:
            calmar_ratio = annualized_return / (abs(max_drawdown) + self.eps)
        else:
            calmar_ratio = np.nan
        self.portfolio_df = port_df
        self.portfolio_metrics = {
            "initial_value": initial_value,
            "final_value(strategy)": final_value,
            "total_return_pct": total_return,
            "annualized_return": annualized_return,
            "annualized_volatility": annualized_vol,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": winrate,
            "loss_trade": lossrate,
            "avg_win": avg_win,
            "avg_loss": avg_loss
        }
        return self.portfolio_metrics, self.portfolio_df