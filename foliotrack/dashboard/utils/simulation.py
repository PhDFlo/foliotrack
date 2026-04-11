import numpy as np


def simulate_contract(contract) -> tuple:
    """
    Simulate yearly portfolio value after applying gross return, Security fee and bank fee.
    """
    # Initialize array to store values at each year
    values = np.empty(contract["years"] + 1)
    values[0] = contract["initial"]
    # Initialize total invested
    invested = contract["initial"]
    # Simulate yearly portfolio value
    for y in range(1, contract["years"] + 1):
        # Apply gross return
        val = values[y - 1] * (1.0 + contract["annual_return"])
        # Apply security expense ratio (reduces return)
        val *= 1.0 - contract["security_fee"]
        # Apply bank annual fee (as % of assets at year end)
        val *= 1.0 - contract["bank_fee"]
        # Add yearly contribution at year end (after fees)
        if contract["yearly_investment"]:
            val += contract["yearly_investment"]
            invested += contract["yearly_investment"]
        # Store value at this year
        values[y] = val
    return values, invested


def compute_after_tax_curve(values, invested, capital_gains_tax) -> np.ndarray:
    """
    Compute after-tax portfolio value at each year.
    """
    # Compute gains
    gains = np.maximum(0.0, values - invested)
    # Compute taxes
    taxes = gains * capital_gains_tax
    # Compute after-tax values
    after_tax = values - taxes
    return after_tax
