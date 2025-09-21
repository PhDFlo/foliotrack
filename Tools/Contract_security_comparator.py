import argparse
import numpy as np
import matplotlib.pyplot as plt


def simulate_contract(
    initial, annual_return, years, security_fee, bank_fee, yearly_contribution=0.0
):
    """
    Simulate yearly portfolio value after applying gross return, Security fee and bank fee.
    Fees (security_fee, bank_fee) are annual percentages (e.g. 0.005 for 0.5%).
    Returns (values_by_year, total_invested).
    values_by_year: numpy array of length (years+1) including year 0 (initial).
    """
    values = np.empty(years + 1)
    values[0] = initial
    invested = initial
    for y in range(1, years + 1):
        # apply gross return
        val = values[y - 1] * (1.0 + annual_return)
        # apply Security expense ratio (reduces return)
        val *= 1.0 - security_fee
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


def compute_after_tax_curve(values, invested, capital_gains_tax):
    """
    Compute after-tax portfolio value at each year, as if liquidated at that year.
    Returns a numpy array of after-tax values (same length as values).
    """
    gains = np.maximum(0.0, values - invested)
    taxes = gains * capital_gains_tax
    after_tax = values - taxes
    return after_tax


def parse_contract_arg(contract_str):
    """
    Parse a contract string of the form:
    "label,security_fee,bank_fee,capgains_tax"
    Example: "A,0.0059,0.006,0.172"
    Returns: dict with keys label, security_fee, bank_fee, capgains_tax
    """
    parts = contract_str.split(",")
    if len(parts) != 4:
        raise ValueError("Contract must be: label,security_fee,bank_fee,capgains_tax")
    label = parts[0].strip()
    security_fee = float(parts[1])
    bank_fee = float(parts[2])
    capgains_tax = float(parts[3])
    return {
        "label": label,
        "security_fee": security_fee,
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
    plt.title("Security investment comparison (fees & capital gains tax)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


def parse_args():
    p = argparse.ArgumentParser(
        description="Compare Security contracts with fees and capital gains tax."
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
        "--yearly_contribution",
        type=float,
        default=0.0,
        help="Yearly contribution added at end of each year",
    )
    p.add_argument(
        "--contract",
        action="append",
        required=True,
        help='Contract definition: "label,security_fee,bank_fee,capgains_tax". \
            Example: --contract "A,0.0059,0.006,0.172" --contract "B,0.0012,0.00,0.30"',
    )
    return p.parse_args()


def find_intersections(xs, curves):
    """
    Find intersection points between all pairs of after-tax curves.
    Returns a list of (x, y) tuples for each intersection, excluding intersections at the initial point.
    """
    intersections = []
    n = len(curves)
    for i in range(n):
        for j in range(i + 1, n):
            curve1 = curves[i]
            curve2 = curves[j]
            diff = curve1 - curve2
            sign_change = np.where(np.diff(np.sign(diff)) != 0)[0]
            for idx in sign_change:
                # Linear interpolation for intersection
                x0, x1 = xs[idx], xs[idx + 1]
                y0_1, y1_1 = curve1[idx], curve1[idx + 1]
                y0_2, y1_2 = curve2[idx], curve2[idx + 1]
                denom = (y1_1 - y0_1) - (y1_2 - y0_2)
                if denom == 0:
                    continue
                t = (y0_2 - y0_1) / denom
                x_cross = x0 + t * (x1 - x0)
                y_cross = y0_1 + t * (y1_1 - y0_1)
                # Exclude intersection at initial point (x=0)
                if x_cross > 0:
                    intersections.append((x_cross, y_cross))
    return intersections


def main():
    args = parse_args()
    contracts = [parse_contract_arg(c) for c in args.contract]
    series_list = []
    invested_list = []
    after_tax_curves = []
    labels = []
    for contract in contracts:
        series, invested = simulate_contract(
            initial=args.initial,
            annual_return=args.annual_return,
            years=args.years,
            security_fee=contract["security_fee"],
            bank_fee=contract["bank_fee"],
            yearly_contribution=args.yearly_contribution,
        )
        after_tax_curve = compute_after_tax_curve(
            series, invested, contract["capgains_tax"]
        )
        series_list.append(series)
        invested_list.append(invested)
        after_tax_curves.append(after_tax_curve)
        labels.append(contract["label"])
        print(
            f"Contract {contract['label']}: pre-withdrawal = {series[-1]:,.2f}, \
                invested = {invested:,.2f}, after-tax = {after_tax_curve[-1]:,.2f}"
        )

    xs = np.arange(0, args.years + 1)
    plt.figure(figsize=(10, 6))
    colors = plt.cm.tab10.colors
    for idx, (series, after_tax_curve, label) in enumerate(
        zip(series_list, after_tax_curves, labels)
    ):
        color = colors[idx % len(colors)]
        plt.plot(
            xs,
            series,
            label=f"{label} (pre-withdrawal)",
            lw=2,
            alpha=0.5,
            linestyle="--",
            color=color,
        )
        plt.plot(xs, after_tax_curve, label=f"{label} (after-tax)", lw=2, color=color)
    # Find and plot intersections between after-tax curves
    intersections = find_intersections(xs, after_tax_curves)
    for x_cross, y_cross in intersections:
        plt.scatter(
            x_cross,
            y_cross,
            marker="o",
            s=80,
            color="black",
            zorder=5,
            label=None,
        )
    plt.xlabel("Years")
    plt.ylabel("Portfolio value")
    plt.title("Security investment comparison (fees & capital gains tax)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
