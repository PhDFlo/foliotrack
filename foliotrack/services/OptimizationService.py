import numpy as np
import cvxpy as cp
import logging
from typing import Tuple
from foliotrack.domain.Portfolio import Portfolio


class OptimizationService:
    """
    Service providing methods to solve for the optimal Security purchase allocation.

    The service models the portfolio rebalancing problem as a Mixed-Integer Quadratic
    Programming (MIQP) problem, specifically focusing on reaching target weights
    while respecting discrete share counts and investment constraints.
    """

    def solve_equilibrium(
        self,
        portfolio: Portfolio,
        investment_amount: float = 1000.0,
        min_percent_to_invest: float = 0.99,
        max_different_securities: int = None,
        selling: bool = False,
    ) -> Tuple[np.ndarray, float, np.ndarray]:
        """
        Solves for the optimal number of units to buy/sell for each Security to
        reach target weights.

        Mathematical Formulation:
        -------------------------
        Let n be the number of securities.
        Variables:
            x ∈ Zⁿ : integer vector representing units to buy for each security.

        Parameters:
            v_old ∈ Rⁿ : vector of current security values (volume * price).
            p ∈ Rⁿ     : vector of current prices.
            P = diag(p) ∈ Rⁿˣⁿ : diagonal matrix of prices.
            w_target ∈ Rⁿ : vector of target weights (shares).
            I_max ∈ R  : total investment amount available.
            α ∈ [0, 1] : minimum fraction of I_max to invest.

        The problem is to minimize the L2 norm of the difference between
        the absolute final values and the total final value scaled by target weights:

        Minimize:
            || (v_old + Px) - [Σᵢ=₁ⁿ (v_old,i + (Px)ᵢ)] * w_target ||₂

        Subject to:
            1. Total new investment: α * I_max ≤ Σᵢ=₁ⁿ (Px)ᵢ ≤ I_max
            2. Discrete shares: xᵢ ∈ Z
            3. Non-negativity (if selling=False): xᵢ ≥ 0
            4. Cardinality: Σᵢ=₁ⁿ zᵢ ≤ K, where zᵢ ∈ {0,1} and |xᵢ| ≤ M * zᵢ

        Args:
            portfolio: The Portfolio domain object to optimize.
            investment_amount: The maximum budget for new investments.
            min_percent_to_invest: Minimum fraction of budget to utilize.
            max_different_securities: Maximum number of distinct securities to hold in the final state.
            selling: If True, allows short selling or reducing existing positions (negative x).

        Returns:
            Tuple containing:
            - security_counts (np.ndarray): Integer units to buy for each security.
            - total_to_invest (float): Actual total amount spent.
            - final_shares (np.ndarray): Resulting allocation weights.
        """

        securities = portfolio.securities
        n = len(securities)
        if n == 0:
            logging.error("Portfolio is empty.")
            raise ValueError("Portfolio is empty.")

        # Set default value for max_different_securities to size of the portfolio
        if max_different_securities is None:
            max_different_securities = n

        # Validate Security attributes
        # (Implicitly valid if using Domain objects properly, but good to check)
        self._validate_securities(securities)

        # Set up optimization variables
        investments, price_matrix, invested_amounts, target_shares = (
            self._setup_optimization_variables(portfolio, n)
        )

        # Set up constraints
        constraints = self._setup_constraints(
            investments,
            price_matrix,
            investment_amount,
            min_percent_to_invest,
            max_different_securities,
            selling,
        )

        # Optimization objective: minimize distance to target weights in absolute value
        # we calculate the absolute error vector and minimize its L2 norm.
        error = cp.norm(
            (invested_amounts + price_matrix @ investments)
            - cp.sum(invested_amounts + price_matrix @ investments) * target_shares,
            2,
        )
        objective = cp.Minimize(error)

        # Build and solve the MIQP problem
        problem = cp.Problem(objective, constraints)
        problem.solve()

        logging.info(f"Optimisation status: {problem.status}")
        if investments.value is None:
            logging.error("Optimization did not produce a solution.")
            raise RuntimeError("Optimization did not produce a solution.")

        # Result is continuous, round to nearest integer as required by discrete shares
        security_counts = np.round(investments.value).astype(int)

        # Update Security objects and collect results
        total_to_invest, final_shares = self._update_security_objects(
            portfolio, security_counts, price_matrix, invested_amounts
        )

        self._log_results(portfolio, total_to_invest)

        return security_counts, total_to_invest, final_shares

    def _validate_securities(self, securities: dict) -> None:
        """
        Verify that all securities have the necessary metadata for optimization.

        Required fields:
        - price_in_portfolio_currency: Current market price.
        - value: Current total value held.
        - name: Display name.
        - symbol: Currency symbol.
        """
        required_attrs = [
            "price_in_portfolio_currency",
            "value",
            "name",
            "symbol",
        ]
        for ticker, security in securities.items():
            for attr in required_attrs:
                if not hasattr(security, attr):
                    raise ValueError(
                        f"Security {ticker} missing required attribute: {attr}"
                    )

    def _setup_optimization_variables(
        self, portfolio: Portfolio, n: int
    ) -> Tuple[cp.Variable, np.ndarray, np.ndarray, np.ndarray]:
        """
        Initializes the CVXPY variables and constant vectors for the optimization.

        Returns:
            investments: Integer CVXPY variable vector.
            price_matrix: Diagonal matrix P of security prices.
            total_value: Vector v_old of current security values.
            target_shares: Vector w_target of target weights.
        """
        investments = cp.Variable(n, integer=True)
        securities_list = list(portfolio.securities.values())  # Ordered list
        price_matrix = np.diag(
            [security.price_in_portfolio_currency for security in securities_list]
        )
        total_value = np.array([security.value for security in securities_list])

        # Read targets from portfolio shares
        target_shares = np.array(
            [portfolio._get_share(s.ticker).target for s in securities_list]
        )
        return investments, price_matrix, total_value, target_shares

    def _setup_constraints(
        self,
        investments: cp.Variable,
        price_matrix: np.ndarray,
        investment_amount: float,
        min_percent_to_invest: float,
        max_non_zero: int,
        selling: bool,
    ) -> list:
        """
        Constructs the constraint list for the solver.

        Implements:
        - Big-M cardinality constraints to limit the number of non-zero positions.
        - Budget constraints (lower and upper bounds on new investment).
        - Integer and transactional constraints (buy-only or buy/sell).
        """
        num_securities = investments.shape[0]
        # Boolean indicator variable for the cardinality constraint
        z = cp.Variable(num_securities, boolean=True)

        prices = np.diag(price_matrix)
        safe_prices = np.where(prices > 0, prices, 1e-9)
        # Big-M bound: roughly allows spending twice the budget on a single security
        upper_bound = (investment_amount / safe_prices) * 2

        base_constraints = [
            # Cardinality constraint: sum of indicators must be ≤ limit
            cp.sum(z) <= max_non_zero,
        ]

        # Actual cash movement tracking
        total_invested_new = cp.sum(price_matrix @ investments)

        if not selling:
            # Constraints for Buy-only scenarios
            return base_constraints + [
                investments >= 0,
                # Tie integer counts to boolean indicators (Big-M)
                investments <= cp.multiply(z, upper_bound),
                # Utilization constraints
                total_invested_new >= min_percent_to_invest * investment_amount,
                total_invested_new <= investment_amount,
            ]
        else:
            # Constraints for Sell-allowed scenarios (x can be negative)
            large_M = 1e6
            return base_constraints + [
                # Bidirectional Big-M linking
                investments <= cp.multiply(z, large_M),
                investments >= -cp.multiply(z, large_M),
                # Utilization constraints
                total_invested_new >= min_percent_to_invest * investment_amount,
                total_invested_new <= investment_amount,
            ]

    def _update_security_objects(
        self,
        portfolio: Portfolio,
        security_counts: np.ndarray,
        price_matrix: np.ndarray,
        invested_amounts: np.ndarray,
    ) -> Tuple[float, np.ndarray]:
        """
        Applies the solved counts to the domain objects and calculates final shares.
        """
        securities_list = list(portfolio.securities.values())
        for i, security in enumerate(securities_list):
            security.volume_to_buy = int(security_counts[i])
            security.amount_to_invest = round(
                price_matrix[i, i] * security_counts[i], 2
            )

        # Vector of final value per security: v_final = v_old + Px
        final_invested = invested_amounts + price_matrix @ security_counts
        total_invested = np.sum(final_invested)
        total_to_invest = float(np.sum(price_matrix @ security_counts))

        # Calculate weight vector: w = v_final / total_v
        if total_invested > 0:
            final_shares = final_invested / total_invested
        else:
            final_shares = np.zeros_like(final_invested)

        # Sync back to portfolio metadata
        for s, val in zip(securities_list, final_shares):
            portfolio._get_share(s.ticker).final = round(float(val), 4)

        return total_to_invest, final_shares

    def _log_results(self, portfolio: Portfolio, total_to_invest: float) -> None:
        """
        Provides detailed logging of the optimization results for audit.
        """
        logging.info("Number of each Security to buy:")
        for security in portfolio.securities.values():
            logging.info(f"  {security.name}: {security.volume_to_buy} units")

        logging.info("Amount to spend and final share of each Security:")
        for ticker, security in portfolio.securities.items():
            logging.info(
                f"  {security.name}: {security.amount_to_invest:.2f}{portfolio.symbol}, Final share = {portfolio.shares[ticker].final:.4f}"
            )
        logging.info(f"Total amount to invest: {total_to_invest:.2f}{portfolio.symbol}")
