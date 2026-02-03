from __future__ import annotations

import os

from DividendCsvReader import DividendCsvReader
from DividendReader import DividendReader
from DividendXlsxReader import DividendXlsxReader


class DividendReaderFactory:
    @staticmethod
    def create_for_path(input_path: str) -> DividendReader:
        extension = DividendReaderFactory._get_extension(input_path)

        if extension in [".csv", ".txt"]:
            return DividendCsvReader()

        if extension == ".xlsx":
            return DividendXlsxReader()

        raise ValueError(
            f"Unsupported dividend input file extension: {extension}. "
            "Supported extensions: .csv, .csv.txt, .xlsx"
        )

    @staticmethod
    def _get_extension(input_path: str) -> str:
        """
        Returns the effective extension for inputs like:
        - file.csv      -> .csv
        - file.csv.txt  -> .txt (so we special-handle .csv.txt below)
        - file.xlsx     -> .xlsx
        """
        filename = os.path.basename(input_path).lower()

        if filename.endswith(".csv.txt"):
            return ".csv"

        _, extension = os.path.splitext(filename)
        return extension
