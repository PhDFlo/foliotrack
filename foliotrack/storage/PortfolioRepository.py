import json
import logging
from typing import Dict, Any
from foliotrack.domain.Portfolio import Portfolio
from foliotrack.domain.Security import Security
from foliotrack.domain.ShareInfo import ShareInfo


class PortfolioRepository:
    """
    Handles persistence of Portfolio objects to/from JSON.
    Preserves the legacy JSON structure where ShareInfo is merged into Security info.
    """

    def save_to_json(self, portfolio: Portfolio, filepath: str) -> None:
        try:
            data = self._to_dict(portfolio)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            logging.info(f"Portfolio saved to {filepath}")
        except Exception as e:
            logging.error(f"Error saving portfolio to JSON: {e}")
            raise

    def load_from_json(self, filepath: str) -> Portfolio:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return self._from_dict(data)
        except Exception as e:
            logging.error(f"Error loading portfolio from JSON: {e}")
            raise

    def _to_dict(self, portfolio: Portfolio) -> Dict[str, Any]:
        securities_dict = {}
        for ticker, security in portfolio.securities.items():
            # Get base security data
            security_info = security.get_info()

            # Get share data
            share_info = portfolio._get_share(ticker)

            # Merge
            security_info.update(share_info.to_dict())

            securities_dict[ticker] = security_info

        return {
            "name": portfolio.name,
            "currency": portfolio.currency,
            "symbol": portfolio.symbol,
            "securities": securities_dict,
            "history": portfolio.history,
        }

    def _from_dict(self, data: Dict[str, Any]) -> Portfolio:
        portfolio = Portfolio(
            name=data.get("name", "Unnamed Portfolio"),
            currency=data.get("currency", "EUR"),
        )

        securities_data = data.get("securities", {})
        history_data = data.get("history", [])

        # Load securities and shares
        if isinstance(securities_data, dict):
            for ticker, security_data in securities_data.items():
                # Extract Share data
                share_data = {
                    "target": security_data.get("target", 0.0),
                    "actual": security_data.get("actual", 0.0),
                    "final": security_data.get("final", 0.0),
                }

                # Construct Security (ignoring share data which isn't in __init__)
                # Security is dataclass, acceptable fields are known.
                # using a helper to filter kwargs would be safer if extra keys exist.
                # Ideally Security.from_dict would handle this, but Security is pure domain now.
                # We can construct it manually or use a helper.
                # Let's map strict fields or use try/except/filter.

                # We need to map dict keys to Security init args.
                # Keys in JSON match Security attributes (ticker, volume etc.)

                # Careful: 'price_in_security_currency' etc might be in JSON.

                # Let's assume JSON keys map to Security fields.
                # Security init args: name, ticker, currency, price_in_security_currency, volume, fill
                # derived fields (symbol, value, etc) are in post_init or manual.

                sec = Security(
                    name=security_data.get("name", "Unnamed Security"),
                    ticker=security_data.get("ticker", "DCAM"),
                    currency=security_data.get("currency", "EUR"),
                    exchange_rate=float(security_data.get("exchange_rate", 1.0)),
                    price_in_security_currency=float(
                        security_data.get("price_in_security_currency", 500.0)
                    ),
                    volume=float(security_data.get("volume", 0.0)),
                    volume_to_buy=float(security_data.get("volume_to_buy", 0.0)),
                    amount_to_invest=float(security_data.get("amount_to_invest", 0.0)),
                    fill=bool(security_data.get("fill", True)),
                )

                # Add to portfolio
                portfolio.securities[ticker] = sec

                # Add share info
                portfolio.shares[ticker] = ShareInfo.from_dict(share_data)

        if isinstance(history_data, list):
            portfolio.history = history_data

        portfolio.recalculate_shares()
        return portfolio
