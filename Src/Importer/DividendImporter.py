from __future__ import annotations

import os

from AppConfig import AppConfig
from DividendReaderFactory import DividendReaderFactory
from KmymoneyXml import KmymoneyXml
from Model.ImportResult import ImportResult


class DividendImporter:
    def __init__(self, cfg: AppConfig):
        self._config = cfg

    def import_dividends(self, *, xml_path: str, input_path: str, out_path: str) -> ImportResult:
        input_filename = os.path.basename(input_path)

        portfolio = self._config.portfolio_for_input_filename(input_filename)
        if portfolio is None:
            raise ValueError(
                f"No portfolio mapping matches input filename: {input_filename}. "
                "Update config.json (filename_contains)."
            )

        reader = DividendReaderFactory.create_for_path(input_path)
        rows = reader.read(input_path)

        kmymoney = KmymoneyXml(xml_path)

        imported_count = 0
        skipped_count = 0
        duplicate_count = 0

        for row in rows:
            security_account_id = portfolio.security_account_for_ticker(row.ticker)
            if security_account_id is None:
                print(f"Skipping row: {row}")
                skipped_count += 1
                continue

            postdate = row.trans_date.isoformat()

            if kmymoney.has_duplicate_dividend(
                postdate=postdate,
                security_account_id=security_account_id,
                amount=row.amount,
                cash_account_id=portfolio.brokerage_cash_account_id,
            ):
                print(f"Skipping row: {row}")
                duplicate_count += 1
                continue

            transaction_id = kmymoney.next_transaction_id()

            kmymoney.add_dividend_transaction(
                row=row,
                transaction_id=transaction_id,
                cash_account_id=portfolio.brokerage_cash_account_id,
                security_account_id=security_account_id,
                income_account_id=portfolio.income_gain_account_id,
            )

            imported_count += 1

        kmymoney.save(out_path)

        return ImportResult(
            imported_count=imported_count,
            skipped_count=skipped_count,
            duplicate_count=duplicate_count,
        )