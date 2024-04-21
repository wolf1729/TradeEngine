import yfinance as yf
import numpy as np
import cvxpy as cp

# Define the tickers for assets in your portfolio
tickers = ['AAPL', 'GOOG', 'MSFT', 'AMZN']

# Download historical stock prices
data = yf.download(tickers, start='2020-01-01', end='2021-01-01')['Adj Close']

# Calculate returns
returns = data.pct_change().dropna()

# Calculate mean returns and covariance matrix
mean_returns = returns.mean()
cov_matrix = returns.cov()

# Define variables
weights = cp.Variable(len(tickers))

# Define objective function - maximize return, minimize risk (volatility)
expected_return = mean_returns.values.T @ weights
risk = cp.quad_form(weights, cov_matrix.values)
objective = cp.Maximize(expected_return - 0.5 * risk)

# Define constraints - weights sum up to 1, individual weights between 0 and 1
constraints = [cp.sum(weights) == 1, weights >= 0, weights <= 1]

# Solve the optimization problem
problem = cp.Problem(objective, constraints)
problem.solve()

# Print optimized portfolio weights
print("Optimized Portfolio Weights:")
print(weights.value)

# Suppose you have initial portfolio weights
initial_weights = np.array([0.25, 0.25, 0.25, 0.25])  # Example initial weights

# Calculate the difference between optimized weights and initial weights
difference = weights.value - initial_weights

# Print recommendations
print("\nRecommendations:")
for i in range(len(tickers)):
    if difference[i] > 0:
        print(f"Buy {tickers[i]}: {difference[i]}")
    elif difference[i] < 0:
        print(f"Sell {tickers[i]}: {abs(difference[i])}")
    else:
        print(f"Hold {tickers[i]}")

# Total investment
total_investment = 10000  # Example total investment amount

# Calculate the amount to invest or divest for each asset
amounts = total_investment * difference

print("\nInvestment/Divestment Amounts:")
for i in range(len(tickers)):
    if amounts[i] > 0:
        print(f"Invest {amounts[i]} in {tickers[i]}")
    elif amounts[i] < 0:
        print(f"Divest {abs(amounts[i])} from {tickers[i]}")
    else:
        print(f"No change in investment for {tickers[i]}")
