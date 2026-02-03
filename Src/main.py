from Importer.AppConfig import AppConfig
from Importer.DividendImporter import DividendImporter

import argparse


def main() -> None:
    """
    Example usage:
      python main.py --xml financesBefore.xml --csv test__AlainRRSP.csv.txt --config config.json --out financesUpdated.xml
    """

    parser = argparse.ArgumentParser(description="Import dividend rows into KMyMoney XML.")
    parser.add_argument("--xml", required=True, help="Path to KMyMoney XML file (input)")
    parser.add_argument("--input", required=True, help="Path to dividend input file (.csv, .csv.txt, .xlsx)")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--out", required=True, help="Path to output XML file")
    args = parser.parse_args()

    cfg = AppConfig.load(args.config)
    importer = DividendImporter(cfg)

    result = importer.import_dividends(
        xml_path=args.xml,
        input_path=args.input,
        out_path=args.out,
    )

    print(f"Imported: {result.imported_count}")
    print(f"Skipped (no mapping / invalid): {result.skipped_count}")
    print(f"Skipped (already exists): {result.duplicate_count}")
    print(f"Output: {args.out}")


if __name__ == "__main__":
    main()
