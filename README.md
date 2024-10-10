# Description

This script calculates the Value at Risk (VaR) and Expected Shortfall (ES) for a portfolio consisting of a single European call option on the S&P 500. The VaR and ES are calculated for a one-day period using historical data.

## Set up

pip install -r requirements.txt

## Run

python var_es_call_option.py

## Run tests

pytest tests.py -v

## Method

Historical S&P 500 price data for the past 10 years is obtained from [1]. This data is used to generate an array of relative prices, defined as P(t)/P(t-1). These relative prices are then used to simulate the next day's price based on today's price. Each simulated price is then applied to the Black-Scholes formula for a European call option. The resulting distribution of profit and loss (PnL) is used to calculate VaR and ES. 

In a real-life scenario, the option price would be determined by market conditions, allowing for the calculation of implied volatility. For simplicity, in this analysis, I used the historical volatility of the S&P 500 and applied a coefficient to simulate the volatility smile.


## Validation

I checked that the initial option price roughly corresponds (within 15%) to the data found in [2].
I plotted the PnL, verifying that since the S&P 500 generally increases over time, the PnL of a call option should also exhibit a positive mean.
The limited number of historical data points is a known limitation, but it was interesting to assess how reliable it is with several thousand points (approximately 252 * 10) that I had. I used generated data to verify that increasing the data points from 10^3 to 10^4 did not significantly affect the results. I ran multiple tests and compared the means. Another approach I considered was randomly selecting a subset of points from the historical data, increasing the sample size gradually, and observing whether the results converge. More work in this direction could definitely be explored.

## Considerations 

1. Other Risk Factors
This analysis focuses primarily on price changes in the option. Other risk factors, such as a change in a perceived future market volatility, are not considered.

2. Corner Cases
I did not focus on edge cases, primarily working with realistic values.

3. Alternative Methods
It would be interesting to explore using historical options data if it were easy to account for differences in strike prices and expiration dates. However, I rejected this approach due to the non-linear nature of options.

# Links
[1] https://www.wsj.com/market-data/quotes/index/SPX/historical-prices
[2] https://www.barchart.com/stocks/quotes/$SPX/options?expiration=2025-10-17-m



