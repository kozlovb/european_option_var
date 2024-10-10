import numpy as np
import scipy.stats as st
# todo use yield ?
import matplotlib.pyplot as plt
# not too much data old data ? 

TRADIG_DAYS_IN_YEAR = 252

def black_scholes_call_price(S, K, T, r, sigma):
    """
    Calculate the Black-Scholes price for a European call option.

    Parameters:
    - S (float): Current price of the underlying asset.
    - K (float): Strike price of the option.
    - T (float): Time to expiration in years.
    - r (float): Risk-free interest rate.
    - sigma (float): Volatility of the underlying asset.

    Returns:
    - call_price (float): Price of the call option based on the Black-Scholes formula.
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * st.norm.cdf(d1) - K * np.exp(-r * T) * st.norm.cdf(d2)
    return call_price

def read_historical_data(file_name):
    """
    Read historical asset prices from a CSV file, reversing the order to 
    get prices from the most recent to the oldest.

    Parameters:
    - file_name (str): The name of the CSV file containing historical prices.

    Returns:
    - prices (np.array): A numpy array of prices from most recent to oldest.
    """
    data_array = np.genfromtxt(file_name, delimiter=',', skip_header=1, dtype=None, encoding='utf-8')
    prices = [row[1] for row in data_array[::-1]]  # Reverse the order of prices
    return np.array(prices)

def get_relative_prices(prices):
    """
    Calculate the daily price change ratios for the asset.

    Parameters:
    - prices (np.array): Array of asset prices.

    Returns:
    - relative_prices (np.array): Array of relative price changes (P(t)/P(t-1)).
    """
    return prices[1:] / prices[:-1]

def calculate_historical_volatility(relative_prices):
    """
    Calculate the annualized historical volatility from daily relative price changes.
    """
    return np.sqrt(TRADIG_DAYS_IN_YEAR) * np.std(relative_prices)

def plot_pnl(pnl):
    """
    Plot the distribution of Profit and Loss (P&L) for a given dataset.

    Parameters:
    - pnl (np.array): Array of P&L values to be plotted.
    """
    plt.figure(figsize=(10, 6))
    
    # Plot histogram of P&L
    plt.hist(pnl, bins=100, color='blue', alpha=0.7, edgecolor='black')

    # Add labels and title
    plt.title('Profit and Loss (P&L) Distribution', fontsize=16)
    plt.xlabel('P&L', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)

    # Show the plot
    plt.grid(True)
    plt.show()

def calculate_var_es(one_day_change, confidence_level_VaR, confidence_level_ES):
    """
    Calculate historical Value at Risk (VaR) and Expected Shortfall (ES) for given P&L.

    Parameters:
    - one_day_change (np.array): Array of daily P&L changes.
    - confidence_level_VaR (float): Confidence level for VaR (e.g., 0.99 for 99%).
    - confidence_level_ES (float): Confidence level for ES (e.g., 0.975 for 97.5%).

    Returns:
    - var (float): The calculated 1-day VaR.
    - es (float): The calculated 1-day Expected Shortfall (ES).
    """
    #TODO do we need to apply np array?
    pnl = np.array(one_day_change)


    var = np.percentile(pnl, (1 - confidence_level_VaR) * 100)

    es_threshold = np.percentile(pnl, (1 - confidence_level_ES) * 100)
    losses_beyond_es_threshold = pnl[pnl <= es_threshold]
    es = losses_beyond_es_threshold.mean() if len(losses_beyond_es_threshold) > 0 else es_threshold
    
    return -var, -es

def simulate_one_day_change(S0, relative_prices, K, T, r, sigma):
    """
    Simulate the change in option prices over one day and calculate the corresponding P&L.

    Parameters:
    - S0 (float): Initial asset price.
    - relative_prices (np.array): Array of daily relative price changes.
    - K (float): Strike price of the option.
    - T (float): Time to expiration in years.
    - r (float): Risk-free interest rate.
    - sigma (float): Volatility of the underlying asset.

    Returns:
    - option_prices (np.array): Array of daily P&L values for the option.
    """
    option_prices = []

    initial_option_price = black_scholes_call_price(S0, K, T, r, sigma)

    for relative_price in relative_prices:

        S = S0 * relative_price

        T_remaining = T - (1 / TRADIG_DAYS_IN_YEAR)

        if T_remaining <= 0:
            raise Exception("Remaining time to expiry is negative")
        
        call_price_end_of_day = black_scholes_call_price(S, K, T_remaining, r, sigma)

        pnl = call_price_end_of_day - initial_option_price

        option_prices.append(pnl)
    
    return np.array(option_prices)

def generate_normal_daily_returns(mean=0.001, std_dev=0.02, size=1000):
    """
    Generator for normally distributed daily returns.
    
    Parameters:
    - mean: The mean of the daily returns (default: 0.001).
    - std_dev: The standard deviation of the daily returns (default: 0.02).
    - size: The number of daily returns to generate (default: 1000). 
    
    Yields:
    - A normally distributed daily return.
    """
    count = 0
    while count < size:
        yield np.random.normal(loc=mean, scale=std_dev)
        count += 1

def volatility_smile(current_price, strike_price, historical_volatility):
    """
    Simple model of volatility smile.
    """

    moneyness = strike_price / current_price

    if moneyness < 0.9:
        adjustment_factor = 1.2  # Increase volatility by 20%
    elif moneyness > 1.1:
        adjustment_factor = 1.3  # Increase volatility by 30%
    else:
        adjustment_factor = 1.0  # No change in volatility

    adjusted_volatility = historical_volatility * adjustment_factor
    
    return adjusted_volatility

def check_parameters(S0, K, T, r, confidence_level_VaR, confidence_level_ES):
    """
    Validate the parameters for calculating the 1-day VaR and ES for a European call option.
    
    Returns:
    - str: An error message if any parameter is invalid, otherwise None.
    """
    
    if S0 <= 0:
        return "Underlying asset price S0 must be positive."

    if K <= 0:
        return "Strike price K must be positive."

    if T < 1 / TRADIG_DAYS_IN_YEAR:
        return "Script doesn't support options that expire earlier than 1 day."

    if not (0 <= r <= 1):
        return "Risk-free rate r must be between 0 and 1"

    if not (0 < confidence_level_VaR < 1):
        return "Confidence level for VaR must be between 0 and 1."
    
    if not (0 < confidence_level_ES < 1):
        return "Confidence level for ES must be between 0 and 1."
    
    return None
