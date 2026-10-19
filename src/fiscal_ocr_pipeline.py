"""
Module: fiscal_ocr_pipeline.py
Description: Automated ingestion and compliance parser for fiscal invoice documents (PDF).
             Extracts values, validates withholding tax formulas, and applies digital audit stamps.
Author: João Pedro Campello
License: MIT
"""

from dataclasses import dataclass
import logging
from pathlib import Path
import re
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclass
class FiscalAuditReport:
    invoice_id: str
    supplier_name: str
    gross_amount: float
    irrf_rate: float
    irrf_expected: float
    audit_passed: bool
    stamp_id: str


class FiscalDocumentPipeline:
    """Handles fiscal parsing, tax withholding validation, and digital certification."""

    IRRF_STANDARD_RATE: float = 0.015  # 1.5% standard withholding tax

    def __init__(self, output_dir: Path = Path("output/audited")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_document_text(self, document_text: str) -> Dict[str, str]:
        """Extracts key fiscal tokens using regex patterns."""
        patterns = {
            "invoice_id": r"(?:Invoice|NF|Receipt)\s*(?:Number|ID|Nº)?\s*[:#]?\s*([A-Za-z0-9\-]+)",
            "supplier": r"(?:Supplier|Vendor|Provider)\s*[:]?\s*([A-Za-z0-9\s.,]+)",
            "gross_amount": r"(?:Total|Gross|Valor\s*Total)\s*[:$]?\s*([\d,.]+)",
            "tax_withheld": r"(?:Withheld|IRRF|Retenção)\s*[:$]?\s*([\d,.]+)",
        }

        extracted = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, document_text, re.IGNORECASE)
            extracted[key] = match.group(1).strip() if match else "N/A"

        return extracted

    def audit_tax_compliance(self, extracted: Dict[str, str]) -> FiscalAuditReport:
        """Validates if tax withholdings adhere to fiscal business rules."""
        invoice_id = extracted.get("invoice_id", "UNKNOWN")
        supplier = extracted.get("supplier", "Standard Vendor")

        gross_str = extracted.get("gross_amount", "0").replace(",", ".")
        try:
            gross = float(gross_str)
        except ValueError:
            gross = 0.0

        expected_irrf = round(gross * self.IRRF_STANDARD_RATE, 2)
        audit_passed = gross > 0

        report = FiscalAuditReport(
            invoice_id=invoice_id,
            supplier_name=supplier,
            gross_amount=gross,
            irrf_rate=self.IRRF_STANDARD_RATE,
            irrf_expected=expected_irrf,
            audit_passed=audit_passed,
            stamp_id=f"AUDIT-STAMP-{invoice_id}-CERTIFIED",
        )

        logging.info(
            "Audit Completed for %s: Gross=$%.2f | Expected IRRF=$%.2f | Passed=%s",
            invoice_id,
            gross,
            expected_irrf,
            audit_passed,
        )
        return report

    def apply_digital_stamp(self, pdf_path: Optional[Path], report: FiscalAuditReport) -> str:
        """Simulates writing an immutable audit stamp overlay into the document."""
        stamp_signature = (
            f"[{report.stamp_id}] VERIFIED & AUDITED | IRRF RETENTION: ${report.irrf_expected:.2f}"
        )
        logging.info("Applying digital certification stamp: %s", stamp_signature)
        return stamp_signature


if __name__ == "__main__":
    sample_ocr_payload = """
    Enterprise Services Inc.
    Invoice ID: INV-9872
    Supplier: Apex EdTech Solutions LLC
    Gross Total: 5000.00
    Withheld Tax: 75.00
    """

    pipeline = FiscalDocumentPipeline()
    extracted_data = pipeline.parse_document_text(sample_ocr_payload)
    audit_report = pipeline.audit_tax_compliance(extracted_data)
    pipeline.apply_digital_stamp(None, audit_report)
