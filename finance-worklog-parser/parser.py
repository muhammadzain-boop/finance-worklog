#!/usr/bin/env python3
"""
Finance Worklog Parser - Reference Implementation
Extracts structured financial data from unstructured sources.
"""

import re
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class WorklogEntry:
    """Represents a single financial worklog entry."""
    activity: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    vendor: Optional[str] = None
    status: Optional[str] = None
    decision: Optional[str] = None
    owner: Optional[str] = None
    date: str = None  # ISO 8601
    due_date: Optional[str] = None
    category: Optional[str] = None
    invoice_number: Optional[str] = None
    blockers: Optional[str] = None
    source: str = "email"
    confidence: str = "high"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class FinanceParser:
    """Parse unstructured financial text into structured worklog entries."""

    # Valid status values
    VALID_STATUSES = [
        "pending", "approved", "rejected", "paid", "received",
        "unknown", "processing", "disputed", "cancelled", "on_hold"
    ]

    # Activity type patterns
    ACTIVITY_PATTERNS = {
        "Invoice Received": r"(?:invoice|bill|statement).*(?:received|attached|attached)",
        "Invoice Approval": r"(?:approved|authorized|proceed|confirmed).*(?:invoice|bill)",
        "Invoice Rejection": r"(?:rejected|denied|declined).*(?:invoice|bill)",
        "Payment Processed": r"(?:payment|paid|sent|processed).*(?:transferred|ach|wire)",
        "Budget Review": r"(?:budget|forecast|review|planning)",
        "Expense Report": r"(?:expense report|reimbursement|submitted expenses)",
    }

    # Currency patterns (USD, EUR, GBP, etc.)
    CURRENCY_PATTERN = r"\b([A-Z]{3})\b|\$|€|£"
    AMOUNT_PATTERN = r"(?:\$|€|£)?\s*(\d+[.,]\d{2}|\d+)"

    def __init__(self):
        self.entries: List[WorklogEntry] = []

    def parse_amount(self, text: str) -> Optional[float]:
        """Extract numeric amount from text."""
        match = re.search(self.AMOUNT_PATTERN, text)
        if match:
            try:
                # Handle both comma and period as decimal separator
                amount_str = match.group(1).replace(",", ".")
                return float(amount_str)
            except ValueError:
                return None
        return None

    def extract_currency(self, text: str) -> Optional[str]:
        """Extract currency code from text."""
        # Check for symbol first
        if "$" in text:
            return "USD"
        elif "€" in text:
            return "EUR"
        elif "£" in text:
            return "GBP"

        # Check for ISO code
        match = re.search(r"\b([A-Z]{3})\b(?:\s+|$)", text)
        if match:
            code = match.group(1)
            # Validate it's a real currency code (simplified check)
            valid_codes = {
                "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF",
                "CNY", "INR", "MXN", "BRL", "ZAR", "SGD", "HKD"
            }
            if code in valid_codes:
                return code

        return None

    def normalize_vendor_name(self, name: str) -> str:
        """Normalize vendor name for consistency."""
        # Remove extra whitespace
        name = " ".join(name.split())
        # Title case
        name = name.title()
        # Remove trailing punctuation
        name = name.rstrip(".,;:")
        return name

    def parse_date(self, date_str: str, reference_date: str = None) -> Optional[str]:
        """Parse various date formats to ISO 8601."""
        if reference_date is None:
            reference_date = datetime.now().isoformat()

        # Try common formats
        formats = [
            "%Y-%m-%d",  # 2026-09-15
            "%m/%d/%Y",  # 09/15/2026 (US)
            "%d/%m/%Y",  # 15/09/2026 (EU)
            "%B %d, %Y",  # September 15, 2026
            "%b %d, %Y",  # Sep 15, 2026
            "%Y-%m-%d %H:%M:%S",  # With time
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # If format not recognized, use reference date with note
        return None

    def detect_activity_type(self, text: str) -> Optional[str]:
        """Detect the type of financial activity from text."""
        text_lower = text.lower()

        for activity_type, pattern in self.ACTIVITY_PATTERNS.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return activity_type

        return "Financial Activity"

    def extract_owner(self, text: str, from_field: str = None) -> Optional[str]:
        """Extract owner/approver name from text."""
        # Look for "Approver:", "Manager:", etc.
        patterns = [
            r"(?:Approver|Approved by|Authorized by|Manager|Owner):\s*([A-Za-z\s]+?)(?:\n|,|$)",
            r"(?:From|Sincerely),?\s*([A-Za-z\s]+?)(?:\n|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                return name if name and len(name) > 1 else None

        # Fall back to from_field if provided
        if from_field and "@" in from_field:
            # Extract name from email
            name = from_field.split("@")[0].replace(".", " ").title()
            return name

        return None

    def detect_status(self, text: str) -> Optional[str]:
        """Detect transaction status from text."""
        text_lower = text.lower()

        status_patterns = {
            "approved": r"(?:approved|authorized|proceed|confirmed)",
            "rejected": r"(?:rejected|denied|declined|cannot approve)",
            "paid": r"(?:paid|sent|processed|transferred|completed)",
            "pending": r"(?:pending|awaiting|waiting|upcoming)",
            "disputed": r"(?:dispute|contested|disagreement)",
        }

        for status, pattern in status_patterns.items():
            if re.search(pattern, text_lower):
                return status

        return None

    def parse_entry(self, text: str, metadata: Dict[str, str] = None) -> WorklogEntry:
        """Parse a text blob into a structured worklog entry."""
        if metadata is None:
            metadata = {}

        # Extract basic fields
        amount = self.parse_amount(text)
        currency = self.extract_currency(text)
        activity = self.detect_activity_type(text)
        status = self.detect_status(text)
        owner = self.extract_owner(text, metadata.get("from"))

        # Parse dates
        date_str = metadata.get("date", datetime.now().isoformat())
        date_iso = self.parse_date(date_str) or datetime.now().strftime("%Y-%m-%d")

        # Extract vendor (look for capitalized words after "from" or in subject)
        vendor = None
        vendor_match = re.search(r"(?:from|vendor):\s*([A-Za-z\s]+?)(?:\n|,|$)", text, re.IGNORECASE)
        if vendor_match:
            vendor = self.normalize_vendor_name(vendor_match.group(1))

        # Extract invoice number
        invoice_match = re.search(r"(?:invoice|bill|ref)[\s#]*:?\s*([A-Z0-9\-]+)", text, re.IGNORECASE)
        invoice_number = invoice_match.group(1) if invoice_match else None

        # Determine confidence
        confidence = "high" if amount and vendor else "medium" if amount or vendor else "low"

        entry = WorklogEntry(
            activity=activity,
            amount=amount,
            currency=currency or "USD",
            vendor=vendor,
            status=status or "unknown",
            owner=owner,
            date=date_iso,
            invoice_number=invoice_number,
            source=metadata.get("source", "email"),
            confidence=confidence
        )

        return entry

    def deduplicate(self, entries: List[WorklogEntry]) -> List[Dict[str, Any]]:
        """Flag likely duplicate entries."""
        duplicates = []

        for i, entry1 in enumerate(entries):
            for j, entry2 in enumerate(entries[i+1:], start=i+1):
                # Same amount, vendor, and date = likely duplicate
                if (entry1.amount == entry2.amount and
                    entry1.vendor == entry2.vendor and
                    entry1.date == entry2.date):
                    duplicates.append({
                        "entry1_index": i,
                        "entry2_index": j,
                        "confidence": "high",
                        "reason": f"Same amount ({entry1.amount}), vendor ({entry1.vendor}), and date ({entry1.date})"
                    })

        return duplicates


def example_usage():
    """Example usage of the parser."""
    parser = FinanceParser()

    # Sample email text
    email_text = """
    From: supplier@acmecorp.com
    Subject: Invoice #INV-2026-1234

    Hi there,

    Please find attached our invoice for the software licenses ordered in August.

    Invoice Number: INV-2026-1234
    Amount: $2,850.00 USD
    Due Date: October 15, 2026
    Description: 10 licenses of SoftwareXYZ for one year

    Best regards,
    Acme Corp Accounting
    """

    metadata = {
        "date": "2026-09-15",
        "from": "supplier@acmecorp.com",
        "source": "email"
    }

    entry = parser.parse_entry(email_text, metadata)
    print(json.dumps(entry.to_dict(), indent=2))


if __name__ == "__main__":
    example_usage()
