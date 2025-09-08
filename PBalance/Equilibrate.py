import numpy as np
import cvxpy as cp
import logging
from typing import List, Tuple, Any


class Equilibrate:
    """
    Provides methods to solve for the optimal Security purchase allocation to match target shares.
    """

    @staticmethod
    def solve_equilibrium(
        securities: List[Any],
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
        n = len(securities)
        if n == 0:
            logging.error("Portfolio is empty.")
            raise ValueError("Portfolio is empty.")

        # Validate Security attributes
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

        investments = cp.Variable(n, integer=True)
        price_matrix = np.diag(
            [security.price_in_portfolio_currency for security in securities]
        )
        invested_amounts = np.array(
            [security.amount_invested for security in securities]
        )
        target_shares = np.array([security.target_share for security in securities])

        constraints = [
            investments >= 0,
            cp.sum(price_matrix @ investments)
            >= min_percent_to_invest * investment_amount,
            cp.sum(price_matrix @ investments) <= investment_amount,
        ]

        error = cp.norm(
            (invested_amounts + price_matrix @ investments)
            - cp.sum(invested_amounts + price_matrix @ investments) * target_shares,
            2,
        )

        objective = cp.Minimize(error)
        problem = cp.Problem(objective, constraints)
        problem.solve()

        logging.info(f"Optimisation status: {problem.status}")
        if investments.value is None:
            logging.error("Optimization did not produce a solution.")
            raise RuntimeError("Optimization did not produce a solution.")
        security_counts = np.round(investments.value).astype(int)

        # Update Security objects and collect results
        for i, security in enumerate(securities):
            security.number_to_buy = int(security_counts[i])

        final_invested = invested_amounts + price_matrix @ security_counts
        total_invested = np.sum(final_invested)
        total_to_invest = float(np.sum(price_matrix @ security_counts))

        if total_invested > 0:
            final_shares = final_invested / total_invested
        else:
            final_shares = np.zeros_like(final_invested)

        for i, security in enumerate(securities):
            security.amount_to_invest = round(
                price_matrix[i, i] * security_counts[i], 2
            )
            security.final_share = round(float(final_shares[i]), 4)

        # Log results
        logging.info("Number of each Security to buy:")
        for i, security in enumerate(securities):
            logging.info(f"  {security.name}: {security.number_to_buy} units")

        logging.info("Amount to spend and final share of each Security:")
        for i, security in enumerate(securities):
            logging.info(
                f"  {security.name}: {security.amount_to_invest:.2f}{security.symbol}, Final share = {security.final_share:.4f}"
            )

        total_amounts = {}
        for security in securities:
            symbol = security.symbol
            total_amounts.setdefault(symbol, 0)
            total_amounts[symbol] += security.amount_to_invest
        logging.info("Total amount to invest:")
        for symbol, amount in total_amounts.items():
            logging.info(f"  {amount:.2f}{symbol}")

        return security_counts, total_to_invest, final_shares
