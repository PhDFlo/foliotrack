import argparse
import numpy as np
import matplotlib.pyplot as plt


def simulate_contract(
    initial, annual_return, years, etf_fee, bank_fee, yearly_contribution=0.0
):
    """
    Simulate yearly portfolio value after applying gross return, ETF fee and bank fee.
    Fees (etf_fee, bank_fee) are annual percentages (e.g. 0.005 for 0.5%).
    Returns (values_by_year, total_invested).
    values_by_year: numpy array of length (years+1) including year 0 (initial).
    """
    values = np.empty(years + 1)
    values[0] = initial
    invested = initial
    for y in range(1, years + 1):
        # apply gross return
        val = values[y - 1] * (1.0 + annual_return)
        # apply ETF expense ratio (reduces return)
        val *= 1.0 - etf_fee
        # apply bank annual fee (as % of assets at year end)
        val *= 1.0 - bank_fee
        # add yearly contribution at year end (after fees)
        if yearly_contribution:
            val += yearly_contribution
            invested += yearly_contribution
        values[y] = val
    return values, invested


def final_after_tax(value, invested, capital_gains_tax):
    """
    Apply capital gains tax on the gains at final withdrawal.
    capital_gains_tax is percentage (e.g. 0.30 for 30%).
    If value <= invested, no tax (no gain).
    """
    gain = max(0.0, value - invested)
    tax = gain * capital_gains_tax
    return value - tax


def parse_contract_arg(contract_str):
    """
    Parse a contract string of the form:
    "label,etf_fee,bank_fee,capgains_tax"
    Example: "A,0.0059,0.006,0.172"
    Returns: dict with keys label, etf_fee, bank_fee, capgains_tax
    """
    parts = contract_str.split(",")
    if len(parts) != 4:
        raise ValueError("Contract must be: label,etf_fee,bank_fee,capgains_tax")
    label = parts[0].strip()
    etf_fee = float(parts[1])
    bank_fee = float(parts[2])
    capgains_tax = float(parts[3])
    return {
        "label": label,
        "etf_fee": etf_fee,
        "bank_fee": bank_fee,
        "capgains_tax": capgains_tax,
    }


def plot_comparison(
    years,
    series_a,
    series_b,
    invested_a,
    invested_b,
    after_tax_a,
    after_tax_b,
    labels=("Contract A", "Contract B"),
):
    xs = np.arange(0, years + 1)
    plt.figure(figsize=(10, 6))
    plt.plot(xs, series_a, label=f"{labels[0]} (pre-withdrawal)", lw=2)
    plt.plot(xs, series_b, label=f"{labels[1]} (pre-withdrawal)", lw=2)
    # mark final after-tax values
    plt.scatter(
        [years],
        [after_tax_a],
        color="C0",
        marker="o",
        s=80,
        label=f"{labels[0]} after tax: {after_tax_a:,.2f}",
    )
    plt.scatter(
        [years],
        [after_tax_b],
        color="C1",
        marker="o",
        s=80,
        label=f"{labels[1]} after tax: {after_tax_b:,.2f}",
    )
    plt.xlabel("Years")
    plt.ylabel("Portfolio value")
    plt.title("ETF investment comparison (fees & capital gains tax)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


def parse_args():
    p = argparse.ArgumentParser(
        description="Compare ETF contracts with fees and capital gains tax."
    )
    p.add_argument("--initial", type=float, default=10000.0, help="Initial investment")
    p.add_argument(
        "--annual-return",
        type=float,
        default=0.06,
        help="Gross annual return (e.g. 0.06 for 6%)",
    )
    p.add_argument("--years", type=int, default=30, help="Number of years to simulate")
    p.add_argument(
        "--contribution",
        type=float,
        default=0.0,
        help="Yearly contribution added at end of each year",
    )
    p.add_argument(
        "--contract",
        action="append",
        required=True,
        help='Contract definition: "label,etf_fee,bank_fee,capgains_tax". Example: --contract "A,0.0059,0.006,0.172" --contract "B,0.0012,0.00,0.30"',
    )
    return p.parse_args()


def main():
    args = parse_args()
    contracts = [parse_contract_arg(c) for c in args.contract]
    series_list = []
    invested_list = []
    after_tax_list = []
    labels = []
    for contract in contracts:
        series, invested = simulate_contract(
            initial=args.initial,
            annual_return=args.annual_return,
            years=args.years,
            etf_fee=contract["etf_fee"],
            bank_fee=contract["bank_fee"],
            yearly_contribution=args.contribution,
        )
        final_pre = series[-1]
        after_tax = final_after_tax(final_pre, invested, contract["capgains_tax"])
        series_list.append(series)
        invested_list.append(invested)
        after_tax_list.append(after_tax)
        labels.append(contract["label"])
        print(
            f"Contract {contract['label']}: pre-withdrawal = {final_pre:,.2f}, invested = {invested:,.2f}, after-tax = {after_tax:,.2f}"
        )

    # Plot all contracts
    xs = np.arange(0, args.years + 1)
    plt.figure(figsize=(10, 6))
    for idx, (series, label, after_tax) in enumerate(
        zip(series_list, labels, after_tax_list)
    ):
        plt.plot(xs, series, label=f"{label} (pre-withdrawal)", lw=2)
        plt.scatter(
            [args.years],
            [after_tax],
            marker="o",
            s=80,
            label=f"{label} after tax: {after_tax:,.2f}",
        )
    plt.xlabel("Years")
    plt.ylabel("Portfolio value")
    plt.title("ETF investment comparison (fees & capital gains tax)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
