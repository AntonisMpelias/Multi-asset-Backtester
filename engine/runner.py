import time
start_time = time.time()


from engine.data_handler import data_handler
from strategies.hybrid_strategy import Hybrid_strat
from engine.asset_weight_assignment import weight_assignment
from engine.risk import killswitch
from engine.performance import performance_metrics
from reports.plots.plotting import plot_portfolio

import numpy as np
import pandas as pd
import yaml

# Load assets
with open("config/assets.yaml", "r") as f:
    asset_list = yaml.safe_load(f)

# Load backtest info (optional, if needed later)
with open("config/backtest.yaml", "r") as f:
    backtest_info = yaml.safe_load(f)

#Isolate specifically the list of assets and not the dictionary that contains it. 
tickers = asset_list['asset_list']

#Isolate the initial investment amount
investment = backtest_info['initial_investment']

#Initialize all the necessary modules including data handling, signal generation and the kill switch
dh = data_handler()
dfs = {}
dfs = dh.data_fetching()
strategy = Hybrid_strat()
ks = killswitch()
#Looping through the modules that take in a single dataframe and not a list (strategy and killswitch)
for company, ticker in tickers.items():
    dfs[ticker] = strategy.on_start(dfs[ticker])
    dfs[ticker]['killswitch'] = ks.on_start(dfs[ticker])
    dfs[ticker]['Signal'] = np.where(dfs[ticker]['killswitch'], 0, dfs[ticker]['Signal'])



#Executing the weight module which can handle a whole list of DFs at once
weight = weight_assignment(dfs)
dfs = weight.weighing_assets()

print("\nCalculating performance portfolio metrics...")

perf = performance_metrics(dfs)
# Calculate the portfolio metrics

portfolio_metrics, portfolio_df = perf.calculating_performance()

SPY_df = dh.SPY_fetching_for_plotting()
#Calculating the returns from the SPY to compare
SPY_returns = SPY_df['Close']/SPY_df['Close'].iloc[0]*investment
SPY_final = 0
SPY_final = SPY_returns.iloc[-1] *1.0

# Print key portfolio metrics to quickly verify results
print("Portfolio Values:\n")

print(f"Initial value= {portfolio_metrics['initial_value']:,.2f}$")
print(f"Final Value (strategy) = {portfolio_metrics['final_value(strategy)']:,.2f}$")
print(f'Final Value(S&P 500)= {SPY_final[-1]:,.2f}$')
print(f"Total return(%) = {portfolio_metrics['total_return_pct']:.2f} %")

print("\nRisk/performance portfolio_metrics:\n")

print(f"Annualized return(%) = {portfolio_metrics['annualized_return']*100:.2f} %")
print(f"Annualized Volatility(%) = {portfolio_metrics['annualized_volatility']*100:.2f}%")
print(f"Sharpe ratio = {portfolio_metrics['sharpe_ratio']:.2f}")
print(f"Sortino ratio = {portfolio_metrics['sortino_ratio']:.2f}")
print(f"Calmar ratio = {portfolio_metrics['calmar_ratio']:.2f}")
print(f"Max drawdown = {portfolio_metrics['max_drawdown']*100:.2f}%\n")

print("\nTrade statistics:\n")

print(f"Win rate = {portfolio_metrics['win_rate']*100:.2f} % ")
print(f"Loss rate = {portfolio_metrics['loss_trade']*100:.2f} % ")
print(f"Average win's profits: {portfolio_metrics['avg_win']*100:.2f}%")
print(f"Average loss' damages: {portfolio_metrics['avg_loss']*100:.2f}%")




plotter = plot_portfolio(
    portfolio_df=portfolio_df,
    metrics=portfolio_metrics,
    spy_df=SPY_df,
    investment=backtest_info['initial_investment'],
    start_date=backtest_info['start_date'],
    end_date=backtest_info['end_date']
)

plot = plotter.plotting()



print("--- Total runtime: %s seconds ---" % (time.time() - start_time))
    
      

