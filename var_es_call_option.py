from helper_functions import (
    read_historical_data,
    get_relative_prices,
    calculate_historical_volatility,
    plot_pnl,
    calculate_var_es,
    simulate_one_day_change,
    volatility_smile,
    check_parameters,
    generate_normal_returns_array,
)

def calculate_one_day_eu_call_option_var_es(S0, K, T, r, confidence_level_VaR, confidence_level_ES, relative_prices, to_plot_pnl=False):
    """
    Calculate the 1-day VaR and ES for a European call option.
    
    Parameters:
    - S0 (float): Current price of the underlying asset.
    - K (float): Strike price of the option.
    - T (float): Time to expiration in years.
    - r (float): Risk-free interest rate.
    - confidence_level_VaR (float): Confidence level for VaR calculation.
    - confidence_level_ES (float): Confidence level for ES calculation.
    - relative_prices (np.array): Array of relative price changes (P(t)/P(t-1)) for 1-day simulation.
    - to_plot_pnl: Whether to plot the P&L distribution, defaults to True.
    
    Returns:
    - var (float): Value at Risk (VaR) for the call option.
    - es (float): Expected Shortfall (ES) for the call option.
    - error_message (str): Error message if any validation or calculation error occurs, otherwise None.
    """
    try:

        err = check_parameters(S0, K, T, r, confidence_level_VaR, confidence_level_ES)
        if err:
            return 0, 0, err

        historical_volatility = calculate_historical_volatility(relative_prices)

        simulated_implied_volatility = volatility_smile(S0, K, historical_volatility)

        one_day_pnl = simulate_one_day_change(S0, relative_prices, K, T, r, simulated_implied_volatility)

        if to_plot_pnl:
            plot_pnl(one_day_pnl)

        var, es = calculate_var_es(one_day_pnl, confidence_level_VaR, confidence_level_ES)

        return var, es, None

    except Exception as e:
        return 0, 0, str(e)

def main():
    # Option parameters
    S0 = 5751.13  # Initial price of the underlying asset
    K = 5800      # Strike price of the option
    T = 1.0       # Time to expiration in years
    r = 0.05      # Risk-free interest rate
    confidence_level_VaR = 0.99  # 99% confidence level for VaR
    confidence_level_ES = 0.975  # 97.5% confidence level for ES

    # Get relative prices from historical data
    relative_prices = get_relative_prices(read_historical_data("SP500_10y.csv"))
    # relative_prices = generate_normal_returns_array()

    # Calculate VaR and ES
    var, es, err = calculate_one_day_eu_call_option_var_es(S0, K, T, r, confidence_level_VaR, confidence_level_ES, relative_prices)
    
    if not err:
        # Print the option parameters only if there is no error
        print("Option parameters:")
        print(f"Initial underlying price (S0): {S0}")
        print(f"Strike price (K): {K}")
        print(f"Time to expiration (T): {T} years")
        print(f"Risk-free interest rate (r): {r}")
        print(f"Confidence level for VaR: {confidence_level_VaR * 100:.1f}%")
        print(f"Confidence level for ES: {confidence_level_ES * 100:.1f}%")
        
        # Print results
        print(f"\nResults:")
        print(f"1-day VaR (99%): {var:.2f}")
        print(f"1-day ES (97.5%): {es:.2f}")
    else:
        print(f"Error: {err}")

if __name__ == "__main__":
    main()

