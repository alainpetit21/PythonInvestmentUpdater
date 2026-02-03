from __future__ import annotations
from typing import List, Optional

import json

from Importer.Model.PortfolioMapping import PortfolioMapping


class AppConfig:
    def __init__(self, portfolios: List[PortfolioMapping]) -> None:
        # Rule 4: constructor only assigns fields
        self._portfolios: List[PortfolioMapping] = portfolios

    @staticmethod
    def load(path: str) -> "AppConfig":
        """
        Factory method responsible for:
        - Reading config file
        - Parsing JSON
        - Building domain objects
        """
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        portfolios: List[PortfolioMapping] = []

        for p in raw.get("portfolios", []):
            portfolios.append(
                PortfolioMapping(
                    name=p["name"],
                    filename_contains=p["filename_contains"],
                    brokerage_cash_account_id=p["brokerage_cash_account_id"],
                    income_gain_account_id=p["income_gain_account_id"],
                    ticker_to_security_account_id={
                        k.upper(): v
                        for k, v in p.get("ticker_to_security_account_id", {}).items()
                    },
                )
            )

        return AppConfig(portfolios)

    def portfolio_for_input_filename(self, filename: str) -> Optional[PortfolioMapping]:
        """
        Returns the first portfolio mapping matching the CSV filename,
        or None if no match exists.
        """
        for portfolio in self._portfolios:
            if portfolio.match_for_filename(filename):
                return portfolio

        return None
