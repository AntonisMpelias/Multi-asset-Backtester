

# Multi-asset backtester
---

This project works as a portfolio wide end-to-end backtesting engine. It includes:

- **Data handling** (Downloading data, saving it locally for efficiency as CSV files, cleaning up NaNs)

- **Signal generation** (Designated strategy folders and files that create signals for every day. Shipped with my own hybrid strategy and risk management but is easily changed.)

- **Portfolio-wide normalized weights** assigned to each asset on each day. They scale inversely with volatility and get a boost if the asset is in a positive trend.

- **A full simulated execution of the deployed strategy** on the selected assets and time period, printing the following **portfolio-wide** aggregated results afterwards:
	+ Sharpe ratio
	+ Sortino ratio
	+ Calmar ratio
	+ Annualized returns (%)
	+ Annualized Volatility (%)
	+ Max drawdown (%)
	+ Starting investment Vs The final portfolio value ($)
- It also prints these trade statistics:
	+ Winrate of trades (%)
	+ Lossrate of trades (%)
	+ Percentage gain from wins (%)
	+ Percentage loss from losses (%)

- **Includes automatically saved and shown plots** to **compare its performance to the S&P 500** during the same time-period for comparable results.
- **Majority of the code is vectorized** to scale well with more assets. (Except the rare python loops that couldn't be avoided when working with multiple dataframes)
___
# Notes
1) The dockerfile works for a quick preview of the strategy's engine as the results described above get printed properly in the terminal, however the plots do not show up on a seperate window as they would if you run it locally. 
2) The included technical overview goes into more detail about the function of this engine and how all the different parts communicate with each other
3) The engine is the main product. The strategy it gets shipped with is undeniably mid, as I had to write it before I started university and therefore could not implement any more sophisticated strategies that rely on higher mathematics

---
# Examples of the plots it produces:
![Examples of plots1](/reports/plots/markdownImage1.png)
![Examples of plots2](/reports/plots/markdownImage2.png)

**This is a personal passion-project. It is not part of a university assignment or anything of that sort. Feel free to use it for your own experimenting, although building an equivalent project from scratch is recommended due to the knowledge you gain from the process.**
