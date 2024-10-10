import numpy as np
from var_es_call_option import calculate_one_day_eu_call_option_var_es

def default_parameters():
    #       S0   K   T   r     var   es
    return 100, 110, 1, 0.05, 0.95, 0.975

def test_price_increases():

    S0, K, T, r, confidence_level_VaR, confidence_level_ES = default_parameters()
    relative_prices = np.linspace(1.01, 1.02, 1000)

    var, es, err = calculate_one_day_eu_call_option_var_es(S0, K, T, r, confidence_level_VaR, confidence_level_ES, relative_prices)

    assert err is None, f"Expected no error, but got: {err}"
    assert var < 0, f"Expected negative VaR (never a loss), but got {var}"
    assert es < 0, f"Expected non-negative ES, but got {es}"

def test_price_decreases():

    S0, K, T, r, confidence_level_VaR, confidence_level_ES = default_parameters()

    relative_prices = np.linspace(0.98, 0.99, 1000)

    var, es, err = calculate_one_day_eu_call_option_var_es(S0, K, T, r, confidence_level_VaR, confidence_level_ES, relative_prices)

    assert err is None, f"Expected no error, but got: {err}"
    assert var > 0, f"Expected positive VaR, but got {var}"
    assert es > 0, f"Expected positive ES, but got {es}"

def test_expiration_within_a_day():

    S0, K, _, r, confidence_level_VaR, confidence_level_ES = default_parameters()
    T = 0.5 / 252  # Less than 1 day
    relative_prices = np.ones(1000)

    _, _, err = calculate_one_day_eu_call_option_var_es(S0, K, T, r, confidence_level_VaR, confidence_level_ES, relative_prices)

    assert err is not None, "Expected an error for options expiring in less than a day, but got None"
