from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PortfolioMapping:
    name: str
    filename_contains: str
    brokerage_cash_account_id: str
    income_gain_account_id: str
    ticker_to_security_account_id: dict[str, str]

    def match_for_filename(self, csv_filename: str) -> bool:
        return self.filename_contains.lower() in csv_filename.lower()

    def security_account_for_ticker(self, ticker: str) -> Optional[str]:
        return self.ticker_to_security_account_id.get(ticker.upper())


