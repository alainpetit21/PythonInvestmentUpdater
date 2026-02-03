from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class DividendRow:
    ticker: str
    trans_date: date
    amount: Decimal
    description: str
    currency: str = "CAD"

