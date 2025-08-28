
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime



class plot_portfolio:
    def __init__(self, portfolio_df, metrics, spy_df, investment, start_date, end_date, label="Portfolio", spy_label="SPY"):
        self.df = portfolio_df
        self.metrics = metrics
        self.spy_df = spy_df.copy()
        self.investment = investment
        self.start_date = start_date
        self.end_date = end_date
        self.label = label
        self.spy_label = spy_label

        # Compute SPY portfolio value for comparison
        self.spy_df['Portfolio_value'] = self.investment * (1 + self.spy_df['Returns'].fillna(0)).cumprod()

    def plotting(self):
        plt.figure(figsize=(12,6))
        plt.plot(self.df['Portfolio_value'], label=self.label, color='black')
        plt.plot(self.spy_df['Portfolio_value'], label=self.spy_label, color='green')
        plt.ylabel('Portfolio Value')
        plt.xlabel('Date')
        plt.legend()
        plt.grid()

        # Overlay the stats box on top of the graph
        textstr = (
            f"Sharpe: {self.metrics['sharpe_ratio']:.2f}\n"
            f"Sortino: {self.metrics['sortino_ratio']:.2f}\n"
            f"Annualized Return: {self.metrics['annualized_return']*100:.2f}%\n"
            f"Final Value: {self.metrics['final_value(strategy)']:,.2f}$\n"
            f"Total Return: {self.metrics['total_return_pct']:,.2f}%"
        )

        plt.text(
            0.02, 0.95, textstr,
            transform=plt.gca().transAxes,
            ha='left', va='top',
            fontsize=10,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )



        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"reports/plots/{self.label}_({self.start_date}...{self.end_date})_{timestamp}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
