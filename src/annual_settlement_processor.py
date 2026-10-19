"""
Module: annual_settlement_processor.py
Description: High-performance processor for massive annual financial reconciliation
             spreadsheets using Pandas and vectorized filtering.
Author: João Pedro Campello
License: MIT
"""

from dataclasses import dataclass
from pathlib import Path
import logging
from typing import Optional
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclass
class SettlementSummary:
    unit_name: str
    reference_period: str
    total_settled: float
    record_count: int
    status: str


class AnnualSettlementProcessor:
    """Processes, filters, and audits high-volume financial settlement records."""

    def __init__(self, data_source: Path):
        self.data_source = Path(data_source)
        self.dataframe: Optional[pd.DataFrame] = None

    def load_dataset(self) -> None:
        """Loads and normalizes the target dataset with optimized data types."""
        if not self.data_source.exists():
            logging.warning("Data file not found. Generating synthetic dataset for execution...")
            self.dataframe = self._generate_mock_dataset()
            return

        logging.info("Reading dataset from: %s", self.data_source)
        self.dataframe = pd.read_excel(
            self.data_source,
            dtype={"unit_code": "category", "period": "str", "status": "category"},
        )
        logging.info("Loaded %d rows successfully.", len(self.dataframe))

    def filter_by_unit(self, unit_name: str, period: Optional[str] = None) -> SettlementSummary:
        """Filters operational records by branch/unit and computes aggregated totals."""
        if self.dataframe is None:
            raise ValueError("Dataset is not loaded. Call load_dataset() first.")

        mask = self.dataframe["unit_name"].str.contains(unit_name, case=False, na=False)
        if period:
            mask = mask & (self.dataframe["period"] == period)

        filtered = self.dataframe[mask]

        if filtered.empty:
            logging.warning("No records matched query for unit: %s", unit_name)
            return SettlementSummary(unit_name, period or "N/A", 0.0, 0, "Not Found")

        total = float(filtered["settled_amount"].sum())
        count = len(filtered)
        status = "Reconciled" if total > 0 else "Pending"

        logging.info("Matched %d records. Total value settled: $ %.2f", count, total)
        return SettlementSummary(unit_name, period or "All", total, count, status)

    @staticmethod
    def _generate_mock_dataset() -> pd.DataFrame:
        """Generates representative mock data for testing and demonstrations."""
        return pd.DataFrame(
            {
                "unit_code": ["U-101", "U-102", "U-101", "U-103", "U-101"],
                "unit_name": [
                    "Regional Unit - Central",
                    "Regional Unit - North",
                    "Regional Unit - Central",
                    "Regional Unit - West",
                    "Regional Unit - Central",
                ],
                "period": ["Sep/2026", "Sep/2026", "Aug/2026", "Sep/2026", "Sep/2026"],
                "settled_amount": [22150.00, 18400.50, 19500.00, 31200.00, 23080.00],
                "status": ["Approved", "Approved", "Approved", "Audited", "Approved"],
            }
        )


if __name__ == "__main__":
    processor = AnnualSettlementProcessor(Path("data/annual_settlement_sample.xlsx"))
    processor.load_dataset()
    summary = processor.filter_by_unit("Regional Unit - Central", period="Sep/2026")
    print("\n--- Summary Result ---")
    print(f"Unit: {summary.unit_name}")
    print(f"Period: {summary.reference_period}")
    print(f"Total Settled: $ {summary.total_settled:,.2f}")
    print(f"Status: {summary.status}")
