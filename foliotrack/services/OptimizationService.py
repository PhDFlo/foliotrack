import numpy as np
import cvxpy as cp
import logging
from typing import Tuple, List
from foliotrack.domain.Portfolio import Portfolio


class OptimizationService:
    """
    Provides methods to solve for the optimal Security purchase allocation.
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
        Solves for the optimal number of each Security to buy.
        Updates each Security object in the portfolio.
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

        # Define the optimization objective
        error = cp.norm(
            (invested_amounts + price_matrix @ investments)
            - cp.sum(invested_amounts + price_matrix @ investments) * target_shares,
            2,
        )
        objective = cp.Minimize(error)

        # Solve
        problem = cp.Problem(objective, constraints)
        problem.solve()

        logging.info(f"Optimisation status: {problem.status}")
        if investments.value is None:
            logging.error("Optimization did not produce a solution.")
            raise RuntimeError("Optimization did not produce a solution.")

        security_counts = np.round(investments.value).astype(int)

        # Update Security objects and collect results
        total_to_invest, final_shares = self._update_security_objects(
            portfolio, security_counts, price_matrix, invested_amounts
        )

        self._log_results(portfolio, total_to_invest)

        return security_counts, total_to_invest, final_shares

    def _validate_securities(self, securities: dict) -> None:
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
        num_securities = investments.shape[0]
        z = cp.Variable(num_securities, boolean=True)

        prices = np.diag(price_matrix)
        safe_prices = np.where(prices > 0, prices, 1e-9)
        upper_bound = (investment_amount / safe_prices) * 2  # Relaxed bound

        base_constraints = [
            cp.sum(z) <= max_non_zero,
        ]

        # Shared constraints logic
        total_invested_new = cp.sum(price_matrix @ investments)

        if not selling:
            return base_constraints + [
                investments >= 0,
                investments <= cp.multiply(z, upper_bound),
                total_invested_new >= min_percent_to_invest * investment_amount,
                total_invested_new <= investment_amount,
            ]
        else:
            large_M = 1e6
            return base_constraints + [
                investments <= cp.multiply(z, large_M),
                investments >= -cp.multiply(z, large_M),
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
        securities_list = list(portfolio.securities.values())
        for i, security in enumerate(securities_list):
            security.volume_to_buy = int(security_counts[i])
            security.amount_to_invest = round(
                price_matrix[i, i] * security_counts[i], 2
            )

        final_invested = invested_amounts + price_matrix @ security_counts
        total_invested = np.sum(final_invested)
        total_to_invest = float(np.sum(price_matrix @ security_counts))

        if total_invested > 0:
            final_shares = final_invested / total_invested
        else:
            final_shares = np.zeros_like(final_invested)

        for s, val in zip(securities_list, final_shares):
            portfolio._get_share(s.ticker).final = round(float(val), 4)

        return total_to_invest, final_shares

    def _log_results(self, portfolio: Portfolio, total_to_invest: float) -> None:
        logging.info("Number of each Security to buy:")
        for security in portfolio.securities.values():
            logging.info(f"  {security.name}: {security.volume_to_buy} units")

        logging.info("Amount to spend and final share of each Security:")
        for ticker, security in portfolio.securities.items():
            logging.info(
                f"  {security.name}: {security.amount_to_invest:.2f}{portfolio.symbol}, Final share = {portfolio.shares[ticker].final:.4f}"
            )
        logging.info(f"Total amount to invest: {total_to_invest:.2f}{portfolio.symbol}")
