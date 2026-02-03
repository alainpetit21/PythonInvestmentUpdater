from dataclasses import dataclass


@dataclass(frozen=True)
class ImportResult:
    imported_count: int
    skipped_count: int
    duplicate_count: int
