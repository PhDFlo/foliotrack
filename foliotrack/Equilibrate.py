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
    ) -> Tuple[np.ndarray, float, np.ndarray]:
        """
        Solves for the optimal number of each Security to buy to approach target shares,
        given a maximum investment. Updates each Security object with the number to buy and
        final share. Returns the solution and logs results.

        Args:
            securities (List[Any]): List of Security objects. Each Security must have attributes:
                - price (float)
                - amount_invested (float)
                - target_share (float)
                - name (str)
                - symbol (str)
            investment_amount (float, optional): Amount to invest. Defaults to 1000.0.
            min_percent_to_invest (float, optional): Minimum percentage of the total investment to consider. Defaults to 0.99.

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

        # Validate Security attributes
        self.validate_securities(securities)

        # Set up optimization variables
        investments, price_matrix, invested_amounts, target_shares = (
            self.setup_optimization_variables(securities, n)
        )

        # Set up constraints
        constraints = self.setup_constraints(
            investments, price_matrix, investment_amount, min_percent_to_invest
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
            securities, security_counts, price_matrix, invested_amounts
        )

        # Log results
        self.log_results(securities, total_to_invest, portfolio.symbol)

        return security_counts, total_to_invest, final_shares

    def validate_securities(self, securities: list) -> None:
        """
        Validates that each Security object has the required attributes.

        Args:
            securities (list): List of Security objects.

        Raises:
            ValueError: If any Security object is missing required attributes.
        """
        required_attrs = [
            "price_in_portfolio_currency",
            "amount_invested",
            "target_share",
            "name",
            "symbol",
        ]
        for security in securities:
            for attr in required_attrs:
                if not hasattr(security, attr):
                    logging.error(f"Security object missing required attribute: {attr}")
                    raise ValueError(
                        f"Security object missing required attribute: {attr}"
                    )

    def setup_optimization_variables(
        self, securities: list, n: int
    ) -> Tuple[cp.Variable, np.ndarray, np.ndarray, np.ndarray]:
        """
        Sets up the optimization variables and matrices.

        Args:
            securities (list): List of Security objects.
            n (int): Number of securities.

        Returns:
            Tuple[cp.Variable, np.ndarray, np.ndarray, np.ndarray]:
                Optimization variables and matrices.
        """
        investments = cp.Variable(n, integer=True)
        price_matrix = np.diag(
            [security.price_in_portfolio_currency for security in securities]
        )
        invested_amounts = np.array(
            [security.amount_invested for security in securities]
        )
        target_shares = np.array([security.target_share for security in securities])
        return investments, price_matrix, invested_amounts, target_shares

    def setup_constraints(
        self,
        investments: cp.Variable,
        price_matrix: np.ndarray,
        investment_amount: float,
        min_percent_to_invest: float,
    ) -> list:
        """
        Sets up the optimization constraints.

        Args:
            investments (cp.Variable): Optimization variable.
            price_matrix (np.ndarray): Price matrix.
            investment_amount (float): Amount to invest.
            min_percent_to_invest (float): Minimum percentage of the total investment to consider.

        Returns:
            list: List of optimization constraints.
        """
        return [
            investments >= 0,
            cp.sum(price_matrix @ investments)
            >= min_percent_to_invest * investment_amount,
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
        securities: list,
        security_counts: np.ndarray,
        price_matrix: np.ndarray,
        invested_amounts: np.ndarray,
    ) -> Tuple[float, np.ndarray]:
        """
        Updates the Security objects with the number to buy and final share.

        Args:
            securities (list): List of Security objects.
            security_counts (np.ndarray): Number of each Security to buy.
            price_matrix (np.ndarray): Price matrix.
            invested_amounts (np.ndarray): Invested amounts.

        Returns:
            Tuple[float, np.ndarray]: Total amount to invest and final shares.
        """
        for i, security in enumerate(securities):
            security.number_to_buy = int(security_counts[i])
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

        for i, security in enumerate(securities):
            security.final_share = round(float(final_shares[i]), 4)

        return total_to_invest, final_shares

    def log_results(
        self, securities: list, total_to_invest: float, portfolio_symbol: str
    ) -> None:
        """
        Logs the results of the optimization.

        Args:
            securities (list): List of Security objects.
            total_to_invest (float): Total amount to invest.
            portfolio_symbol (str): Portfolio symbol.
        """
        logging.info("Number of each Security to buy:")
        for i, security in enumerate(securities):
            logging.info(f"  {security.name}: {security.number_to_buy} units")

        logging.info("Amount to spend and final share of each Security:")
        for i, security in enumerate(securities):
            logging.info(
                f"  {security.name}: {security.amount_to_invest:.2f}{portfolio_symbol}, Final share = {security.final_share:.4f}"
            )

        total_amount = 0.0
        for security in securities:
            total_amount += security.amount_to_invest
        logging.info(f"Total amount to invest: {total_amount:.2f}{portfolio_symbol}")


_EQUILIBRIUM = Equilibrate()

solve_equilibrium = _EQUILIBRIUM.solve_equilibrium
