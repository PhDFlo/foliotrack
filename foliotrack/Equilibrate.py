import numpy as np
import cvxpy as cp
import logging
from typing import Tuple
from .Portfolio import Portfolio


class Equilibrate:
    """
    Provides methods to solve for the optimal Security purchase allocation to match target shares.
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
        Solves for the optimal number of each Security to buy to approach target shares,
        given a maximum investment. Updates each Security object with the number to buy and
        final share. Returns the solution and logs results.

        Args:
            portfolio (Portfolio): Portfolio object containing the securities to be optimized.
            investment_amount (float, optional): Amount to invest. Defaults to 1000.0.
            min_percent_to_invest (float, optional): Minimum percentage of the total investment to consider. Defaults to 0.99.
            max_different_securities (int, optional): Maximum number of different securities to consider. Defaults to size of the portfolio.
            selling (bool, optional): Whether selling is allowed. Maximizes target shares but not investment. Defaults to False.

        Returns:
            Tuple[np.ndarray, float, np.ndarray]:
                - security_counts: Number of each Security to buy (int array)
                - total_to_invest: Total amount to invest (float)
                - final_shares: Final share of each Security (float array)

        Raises:
            ValueError: If Security list is empty or required attributes are missing.
            RuntimeError: If optimization fails.
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
        self.validate_securities(securities)

        # Set up optimization variables
        investments, price_matrix, invested_amounts, target_shares = (
            self.setup_optimization_variables(portfolio, n)
        )

        # Set up constraints
        constraints = self.setup_constraints(
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

        # Solve the optimization problem
        problem = self.solve_optimization_problem(objective, constraints)

        logging.info(f"Optimisation status: {problem.status}")
        if investments.value is None:
            logging.error("Optimization did not produce a solution.")
            raise RuntimeError("Optimization did not produce a solution.")
        security_counts = np.round(investments.value).astype(int)

        # Update Security objects and collect results
        total_to_invest, final_shares = self.update_security_objects(
            portfolio, security_counts, price_matrix, invested_amounts
        )

        # Log results
        self.log_results(portfolio, total_to_invest)

        return security_counts, total_to_invest, final_shares

    def validate_securities(self, securities: dict) -> None:
        """
        Validates that each Security object has the required attributes.

        Args:
            securities (dict): Dictionary of Security objects keyed by ticker.

        Raises:
            ValueError: If any Security object is missing required attributes.
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
                    logging.error(
                        f"Security {ticker} missing required attribute: {attr}"
                    )
                    raise ValueError(
                        f"Security {ticker} missing required attribute: {attr}"
                    )

    def setup_optimization_variables(
        self, portfolio: Portfolio, n: int
    ) -> Tuple[cp.Variable, np.ndarray, np.ndarray, np.ndarray]:
        """
        Sets up the optimization variables and matrices.

        Args:
            portfolio (Portfolio): The portfolio containing securities and target shares.
            n (int): Number of securities.

        Returns:
            Tuple[cp.Variable, np.ndarray, np.ndarray, np.ndarray]:
                Optimization variables and matrices.
        """
        investments = cp.Variable(n, integer=True)
        # Convert dictionary values to ordered lists
        securities_list = list(portfolio.securities.values())
        price_matrix = np.diag(
            [security.price_in_portfolio_currency for security in securities_list]
        )
        total_value = np.array([security.value for security in securities_list])
        # Read target shares from the portfolio using helper (ordered by securities)
        target_shares = np.array(
            [portfolio._get_share(s.ticker).target for s in securities_list]
        )
        return investments, price_matrix, total_value, target_shares

    def setup_constraints(
        self,
        investments: cp.Variable,
        price_matrix: np.ndarray,
        investment_amount: float,
        min_percent_to_invest: float,
        max_non_zero: int,
        selling: bool,
    ) -> list:
        """
        Sets up the optimization constraints.

        Args:
            investments (cp.Variable): Optimization variable.
            price_matrix (np.ndarray): Price matrix.
            investment_amount (float): Amount to invest.
            min_percent_to_invest (float): Minimum percentage of the total investment to consider.
            max_non_zero (integer): Maximum number of elements that can be non zero.
            selling (bool): Whether selling is allowed.

        Returns:
            list: List of optimization constraints.
        """
        num_securities = investments.shape[0]
        z = cp.Variable(num_securities, boolean=True)
        
        # Extract prices from the diagonal of the price matrix
        prices = np.diag(price_matrix)
        
        # Calculate Big-M bounds
        # For buying, the max we can buy is investment_amount / price
        # We add a small buffer for numerical stability if needed, though integer constraints usually handle it.
        # Ensure we don't divide by zero if price is 0 (should shouldn't happen in valid portfolio)
        safe_prices = np.where(prices > 0, prices, 1e-9)
        upper_bound = investment_amount / safe_prices

        # Base constraints
        base_constraints = [
            cp.sum(z) <= max_non_zero,
        ]

        if not selling:
            # Buying only
            return base_constraints + [
                investments >= 0,
                investments <= cp.multiply(z, upper_bound),
                cp.sum(price_matrix @ investments) >= min_percent_to_invest * investment_amount,
                cp.sum(price_matrix @ investments) <= investment_amount,
            ]
        else:
            # Selling allowed
            # We need a large M for lower/upper bound when selling is allowed since we don't assume holdings here.
            # Using a sufficiently large number, or perhaps derived from total portfolio value if available.
            # Since we lack context, we'll use a large constant relative to investment or just a fixed large M.
            large_M = 1e6  # Arbitrary large bound for selling context
            return base_constraints + [
               investments <= cp.multiply(z, large_M),
               investments >= -cp.multiply(z, large_M),
               cp.sum(price_matrix @ investments) >= min_percent_to_invest * investment_amount,
               cp.sum(price_matrix @ investments) <= investment_amount,
            ]

    def solve_optimization_problem(
        self, objective: cp.Minimize, constraints: list
    ) -> cp.Problem:
        """
        Solves the optimization problem.

        Args:
            objective (cp.Minimize): Optimization objective.
            constraints (list): List of optimization constraints.

        Returns:
            cp.Problem: Solved optimization problem.
        """
        problem = cp.Problem(objective, constraints)
        problem.solve()
        return problem

    def update_security_objects(
        self,
        portfolio: Portfolio,
        security_counts: np.ndarray,
        price_matrix: np.ndarray,
        invested_amounts: np.ndarray,
    ) -> Tuple[float, np.ndarray]:
        """
        Updates the Security objects with the number to buy and final share.

        Args:
            portfolio (Portfolio): Portfolio containing the securities to update.
            security_counts (np.ndarray): Number of each Security to buy.
            price_matrix (np.ndarray): Price matrix.
            invested_amounts (np.ndarray): Invested amounts.

        Returns:
            Tuple[float, np.ndarray]: Total amount to invest and final shares.
        """
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

        # Write final shares back into portfolio shares mapping
        for s, val in zip(securities_list, final_shares):
            portfolio._get_share(s.ticker).final = round(float(val), 4)

        return total_to_invest, final_shares

    def log_results(self, portfolio: Portfolio, total_to_invest: float) -> None:
        """
        Logs the results of the optimization.

        Args:
            portfolio (Portfolio): The portfolio containing securities and shares.
            total_to_invest (float): Total amount to invest.
        """
        logging.info("Number of each Security to buy:")
        for security in portfolio.securities.values():
            logging.info(f"  {security.name}: {security.volume_to_buy} units")

        logging.info("Amount to spend and final share of each Security:")
        for ticker, security in portfolio.securities.items():
            logging.info(
                f"  {security.name}: {security.amount_to_invest:.2f}{portfolio.symbol}, Final share = {portfolio.shares[ticker].final:.4f}"
            )

        total_amount = sum(
            security.amount_to_invest for security in portfolio.securities.values()
        )
        logging.info(f"Total amount to invest: {total_amount:.2f}{portfolio.symbol}")


_EQUILIBRIUM = Equilibrate()

solve_equilibrium = _EQUILIBRIUM.solve_equilibrium
