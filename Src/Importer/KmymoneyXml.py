from __future__ import annotations
from datetime import datetime
from decimal import Decimal

import xml.etree.ElementTree as ElementTree
import re

from Importer.Model.DividendRow import DividendRow


class KmymoneyXml:
    """
    Minimal KMyMoney XML writer for dividend transactions.

    Assumptions based on typical KMyMoney XML structure:
    - A <TRANSACTIONS> container exists
    - Transactions are <TRANSACTION ...> children
    """

    TX_ID_RE = re.compile(r"^T(\d+)$")

    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.tree = ElementTree.parse(xml_path)
        self.root = self.tree.getroot()
        self.paths = self._locate_paths()

    def _locate_paths(self) -> ElementTree.Element:
        # Common: <KMYMONEY-FILE> ... <TRANSACTIONS> ... <TRANSACTION/>
        tx_root = self.root.find(".//TRANSACTIONS")

        if tx_root is None:
            raise ValueError("Could not find <TRANSACTIONS> in KMyMoney XML.")

        return tx_root

    def save(self, out_path: str) -> None:
        self._indent(self.root)

        xml_body = ElementTree.tostring(
            self.root,
            encoding="utf-8",
            xml_declaration=True
        ).decode("utf-8")

        doctype = "<!DOCTYPE KMYMONEY-FILE>\n"

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(xml_body.replace("\n<KMYMONEY-FILE>", f"\n{doctype}<KMYMONEY-FILE>", 1))

    def next_transaction_id(self) -> str:
        max_num = 0
        for tx in self.paths.findall("./TRANSACTION"):
            tx_id = tx.get("id", "")
            m = self.TX_ID_RE.match(tx_id)

            if m:
                max_num = max(max_num, int(m.group(1)))

        # Keep KMyMoney-style padding: "T000000000000023867"
        return f"T{max_num + 1:018d}"

    def has_duplicate_dividend(
        self,
        *,
        postdate: str,
        security_account_id: str,
        amount: Decimal,
        cash_account_id: str,
    ) -> bool:
        """
        Simple duplicate heuristic:
        - Same postdate
        - Has a split with action='Dividend' on the security account
        - Has cash split in cash account with matching amount
        """
        target_amt = self._decimal_to_kmm_rational(amount)

        for tx in self.paths.findall("./TRANSACTION"):
            if tx.get("postdate") != postdate:
                continue

            splits = tx.findall("./SPLITS/SPLIT")
            saw_security_div = any(
                (s.get("account") == security_account_id and s.get("action") == "Dividend")
                for s in splits
            )
            if not saw_security_div:
                continue

            saw_cash = any(
                (s.get("account") == cash_account_id and s.get("value") == target_amt)
                for s in splits
            )
            if saw_cash:
                return True

        return False

    def add_dividend_transaction(
        self,
        *,
        row: DividendRow,
        transaction_id: str,
        cash_account_id: str,
        security_account_id: str,
        income_account_id: str,
    ) -> None:
        """
        Create a 3-split KMyMoney dividend transaction:
          1) Cash account: +amount
          2) Security account: action='Dividend', value 0 (or amount, depends on prefs; we keep 0)
          3) Income account: -amount
        """

        print(f"Adding dividend transaction: {row}")
        postdate = row.trans_date.isoformat()
        now = self._kmm_datetime_now()

        tx = ElementTree.Element(
            "TRANSACTION",
            {
                "id": transaction_id,
                "postdate": postdate,
                "memo": row.description,
                "commodity": row.currency,
                "entrydate": now,
                "modified": now,
            },
        )

        splits_el = ElementTree.SubElement(tx, "SPLITS")
        amt = self._decimal_to_kmm_rational(row.amount)
        neg_amt = self._decimal_to_kmm_rational(-row.amount)

        # Split 1: cash +amount
        ElementTree.SubElement(
            splits_el,
            "SPLIT",
            {
                "id": "S0001",
                "account": cash_account_id,
                "value": amt,
                "shares": amt,
                "memo": row.description,
            },
        )

        # Split 2: security action Dividend (value often 0; keep explicit Dividend tag)
        ElementTree.SubElement(
            splits_el,
            "SPLIT",
            {
                "id": "S0002",
                "account": security_account_id,
                "value": "0/1",
                "shares": "0/1",
                "action": "Dividend",
                "memo": row.description,
            },
        )

        # Split 3: income -amount
        ElementTree.SubElement(
            splits_el,
            "SPLIT",
            {
                "id": "S0003",
                "account": income_account_id,
                "value": neg_amt,
                "shares": neg_amt,
                "memo": row.description,
            },
        )

        self.paths.append(tx)

    def _decimal_to_kmm_rational(self, value: Decimal) -> str:
        """
        Converts Decimal dollars to a rational like '1219/100' for cents.
        Assumes 2 decimal places for CAD/USD style currencies.
        """
        cents = int((value * Decimal("100")).to_integral_value())
        return f"{cents}/100"

    def _kmm_datetime_now(self) -> str:
        # Often KMyMoney uses: YYYY-MM-DDThh:mm:ss
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _indent(self, elem: ElementTree.Element, level: int = 0) -> None:
        # Pretty printing for readability
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for child in elem:
                self._indent(child, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
