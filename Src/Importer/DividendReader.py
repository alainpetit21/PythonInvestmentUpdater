from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from Model.DividendRow import DividendRow


class DividendReader(ABC):
    @abstractmethod
    def read(self, input_path: str) -> List[DividendRow]:
        """
        Reads a dividend input file and returns a list of parsed DividendRow objects.

        Implementations:
        - DividendCsvReader
        - DividendXlsxReader
        """
        raise NotImplementedError