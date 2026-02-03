from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional

import csv

from DividendReader import DividendReader
from Model.DividendRow import DividendRow


class DividendCsvReader(DividendReader):
    """
    Reads dividend lines from a CSV export.

    You may need to adapt column names depending on your bank export:
    - ticker/symbol: "Symbol" or "Ticker"
    - date: "Transaction Date" or "Settlement Date" or "Date"
    - amount: "Net Amount" or "Amount"
    - description: "Description"
    """

    def read(self, input_path: str) -> List[DividendRow]:
        rows: List[DividendRow] = []

        with open(input_path, "r", encoding="utf-8-sig", newline="") as file_handle:
            reader = csv.DictReader(file_handle)

            for raw_row in reader:
                dividend_row = self._parse_row(raw_row)
                if dividend_row is None:
                    continue

                rows.append(dividend_row)

        return rows

    def _parse_row(self, raw_row: Dict[str, str]) -> Optional[DividendRow]:
        ticker = self._parse_ticker(raw_row)
        if ticker is None:
            return None

        trans_date = self._parse_date(raw_row)
        if trans_date is None:
            return None

        amount = self._parse_amount(raw_row)
        if amount is None:
            return None

        description = raw_row.get("Description") or raw_row.get("Action") or "Dividend"
        currency = raw_row.get("Currency") or "CAD"

        return DividendRow(
            ticker=ticker,
            trans_date=trans_date,
            amount=amount,
            description=description.strip(),
            currency=currency.strip().upper(),
        )

    def _parse_ticker(self, raw_row: Dict[str, str]) -> Optional[str]:
        ticker = (
            raw_row.get("Symbol")
            or raw_row.get("Ticker")
            or raw_row.get("symbol")
        )

        if ticker is None:
            return None

        ticker = ticker.strip().upper()

        if not ticker:
            return None

        return ticker

    def _parse_date(self, raw_row: Dict[str, str]) -> Optional[datetime.date]:
        date_str = (
            raw_row.get("Transaction Date")
            or raw_row.get("Settlement Date")
            or raw_row.get("Date")
        )

        if date_str is None:
            return None

        date_str = date_str.strip()

        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%d %I:%M:%S %p",
        ]

        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format).date()
            except ValueError:
                continue

        return None

    def _parse_amount(self, raw_row: Dict[str, str]) -> Optional[Decimal]:
        amount_str = (
            raw_row.get("Net Amount")
            or raw_row.get("Amount")
            or raw_row.get("amount")
        )

        if amount_str is None:
            return None

        amount_str = (
            amount_str
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

        if not amount_str:
            return None

        try:
            return Decimal(amount_str)
        except Exception:
            return None