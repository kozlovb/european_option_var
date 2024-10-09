import numpy as np
import scipy.stats as st
# todo use yield ?
import matplotlib.pyplot as plt
# not too much data old data ? 


TRADIG_DAYS_IN_YEAR = 252

#TODO exceptions may be
#TODO add docs
# todo discuss risks
#TODO add tests

def read_historical_data(file_name):
    data_array = np.genfromtxt(file_name, delimiter=',', skip_header=1, dtype=None, encoding='utf-8')
    print(data_array)
    prices = [row[1] for row in data_array]
    return np.array(prices)

### comments everywhere ? function name return value etc
def get_relative_prices(prices):
    # Calculate price change ratios
    return prices[1:] / prices[:-1]

def calculate_historical_volatility(relative_prices):
    # Step 2: Compute daily volatility (standard deviation of simple returns)
    return np.sqrt(TRADIG_DAYS_IN_YEAR) * np.std(relative_prices)
#TODO plug it 
def volatility_smile(strike_price, current_price, historical_volatility):
    """
    Simple model of volatility smile.
    
    Parameters:
    strike_price (float): The strike price of the option
    current_price (float): The current price of the underlying asset
    historical_volatility (float): The historical annualized volatility
    
    Returns:
    adjusted_volatility (float): Volatility adjusted for the smile effect
    """
    
    # Moneyness is how far the strike is from current price
    moneyness = strike_price / current_price
    
    # Use a simple quadratic adjustment: more extreme moneyness gets higher volatility
    if moneyness < 0.9:  # Deep ITM (strike price is much lower than current price)
        adjustment_factor = 1.2  # Increase volatility by 20%
    elif moneyness > 1.1:  # Deep OTM (strike price is much higher than current price)
        adjustment_factor = 1.3  # Increase volatility by 30%
    else:  # Near ATM (strike price close to current price)
        adjustment_factor = 1.0  # No change in volatility
    
    # Adjust the historical volatility
    adjusted_volatility = historical_volatility * adjustment_factor
    
    return adjusted_volatility

# Black-Scholes formula for a European call option
def black_scholes_call_price(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * st.norm.cdf(d1) - K * np.exp(-r * T) * st.norm.cdf(d2)
    return call_price

# Simulate future asset prices using historical returns or normally distributed returns


def generate_normal_daily_returns(mean=0.001, std_dev=0.02, size=1000):
    """
    Generator for normally distributed daily returns.
    
    Parameters:
    - mean: The mean of the daily returns (default: 0.001).
    - std_dev: The standard deviation of the daily returns (default: 0.02).
    - size: The number of daily returns to generate. If None, will generate indefinitely.
    
    Yields:
    - A normally distributed daily return.
    """
    count = 0
    while count < size:
        yield np.random.normal(loc=mean, scale=std_dev)
        count += 1


# Simulate option prices
def simulate_asset_prices(S0, relative_prices, K, T, r, sigma):
    option_prices = []

    # Loop over daily returns
    for relative_price in relative_prices:

        S = S0 * (relative_price)  #correct or not ? 
        
        # Update time to maturity (reduce by 1 day each step)
        T_remaining = T - (1) / TRADIG_DAYS_IN_YEAR  # Assuming 252 trading days in a year
        
        # Ensure T does not become negative TODO just not allow options like this
        if T_remaining <= 0:
            T_remaining = 0.0001  # Avoid zero division error in Black-Scholes
        
        # Calculate option price using Black-Scholes
        call_price = black_scholes_call_price(S, K, T_remaining, r, sigma)
        
        # Append calculated option price to the list
        option_prices.append(call_price)
    
    return np.array(option_prices)

def plot_pnl(pnl):
    plt.figure(figsize=(10, 6))
    
    # Plot histogram of P&L
    plt.hist(pnl, bins=50, color='blue', alpha=0.7, edgecolor='black')

    # Add labels and title
    plt.title('Profit and Loss (P&L) Distribution', fontsize=16)
    plt.xlabel('P&L', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)

    # Show the plot
    plt.grid(True)
    plt.show()

# Historical Simulation for VaR and ES
def historical_var_es(option_prices, K, T, r, sigma, confidence_level_VaR, confidence_level_ES, initial_option_price):
    pnl  =  np.array(option_prices)  - initial_option_price
    plot_pnl(pnl)

    # Calculate VaR using the specified confidence level
    var = np.percentile(pnl, (1 - confidence_level_VaR) * 100)
    
    # Here, you might choose to calculate ES based on a different confidence level
    # For example, you can use confidence_level_ES to determine a threshold
    es_threshold = np.percentile(pnl, (1 - confidence_level_ES) * 100)
    losses_beyond_es_threshold = pnl[pnl <= es_threshold]
    es = losses_beyond_es_threshold.mean() if len(losses_beyond_es_threshold) > 0 else es_threshold
    return var, es, pnl

def plot_simulated_prices(simulated_prices):
    plt.figure(figsize=(10, 6))
    
    # Plot histogram of the final simulated prices after 1 day
    plt.hist(simulated_prices[:, -1], bins=50, color='green', alpha=0.7, edgecolor='black')

    # Add labels and title
    plt.title('1-Day Simulated Asset Price Distribution', fontsize=16)
    plt.xlabel('Price', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)

    # Show the plot
    plt.grid(True)
    plt.show()
#TODO add doc on how install libs
# Main function
def main():
    # Option parameters
    S0 = 5751.13  # Initial price of the underlying asset
    K = 5750  # Strike price of the option
    T = 30/365  # Time to expiration in years (30 days)
    r = 0.05  # Risk-free interest rate
    sigma = 0.2  # Volatility (increased for more variation)
    confidence_level_VaR = 0.99  # 99% confidence level for VaR
    confidence_level_ES = 0.975  # 97.5% confidence level for ES
   
    relative_prices = get_relative_prices(read_historical_data("SP500_10y.csv"))
    historical_volatility = calculate_historical_volatility(relative_prices)
    print("historical_volatility", historical_volatility)
    simulated_implied_volatility = volatility_smile(K, S0, historical_volatility)

    # here can plug  a generator
    option_prices_historical_simulation = simulate_asset_prices(S0, relative_prices, K, T, r, simulated_implied_volatility)
    initial_option_price = black_scholes_call_price(S0, K, T, r, sigma)

    var, es, pnl = historical_var_es(option_prices_historical_simulation, K, T, r, simulated_implied_volatility, confidence_level_VaR, confidence_level_ES, initial_option_price)

    # Print results
    print(f"1-day VaR (99%): {var:.2f}")
    print(f"1-day ES (97.5%): {es:.2f}")

# Run the main code
if __name__ == "__main__":
    main()
