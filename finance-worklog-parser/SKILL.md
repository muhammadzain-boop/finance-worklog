---
name: finance-worklog-parser
description: Use when extracting financial activities from unstructured sources (emails, meeting transcripts, Slack messages) to build structured work logs
---

# Finance Worklog Parser

## Overview

Parse unstructured financial communications into structured worklog entries. Automatically extract amounts, vendors, statuses, decisions, and blockers from emails, transcripts, and messages—converting communication noise into audit-ready records.

**Core principle:** Every financial decision happens in communication channels. Capture it before it's lost.

## When to Use

Triggered by financial activities entering your system:
- Email invoices, approval chains, payment confirmations
- Meeting transcripts discussing budgets, forecasts, expense reviews
- Slack conversations about invoice status, approvals, blockers
- Uploaded receipts, statements, or financial documents

**When NOT to use:** Structured data already in accounting software (don't parse what's already recorded)

## Quick Reference: What to Extract

| Field | Source | Example |
|-------|--------|---------|
| **Activity** | Email subject/transcript content | "Invoice Approval", "Budget Review", "Payment Processed" |
| **Amount** | Email body, receipt, transaction | $5,400 |
| **Vendor/Party** | Email from/to, meeting attendees | "Acme Corp", "Finance Team" |
| **Status** | Keywords in content | approved, pending, rejected, processing |
| **Decision** | Main action taken | "Approved for Q4 budget", "Rejected - exceeds limit" |
| **Blocker** | Issues preventing progress | "Waiting for manager sign-off", "Missing receipt" |
| **Owner** | Who made decision/who responsible | Sarah Chen, Finance Manager |
| **Date** | Email date, transcript timestamp | 2026-09-15 |
| **Category** | Inferred from vendor/type | Equipment, Travel, Consulting |

## Extraction Workflow

### Step 1: Identify Activity Type
Read the source. Match against patterns:
- **Approval Activity**: "Approved", "Rejected", "Pending approval"
- **Payment Activity**: "Paid", "Processed", "Sent payment"
- **Review Activity**: "Budget review", "Forecasted", "Analyzed spending"
- **Alert Activity**: "Unusual spending", "Duplicate charge", "Late payment"

### Step 2: Extract Core Fields

```json
{
  "activity": "Invoice Approval",
  "amount": 5400,
  "currency": "USD",
  "vendor": "Acme Corp",
  "status": "approved",
  "decision": "Approved for Q4 equipment budget",
  "owner": "Sarah Chen",
  "date": "2026-09-15",
  "category": "Equipment"
}
```

### Step 3: Handle Edge Cases

**Multi-currency amounts:**
- Extract value: $5,400
- Mark currency: USD
- If conversion needed, flag for reference rate lookup

**Missing data:**
- DON'T invent fields
- Mark as "not_found" or null
- Flag for follow-up in blocker

**Ambiguous status:**
- Use most conservative interpretation
- "Should approve" = pending (not approved)
- "We approved" = approved

**Multiple activities in one message:**
- Parse each as separate entry
- Link with source_message_id

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Extracting from already-recorded transactions | Don't parse data already in accounting system |
| Adding fields that aren't in source | Extract only what's explicit; flag unknowns as blocker |
| Guessing vendor name variants | Use exact name from email; normalize in reference step |
| Confusing "requested" with "approved" | Treat as pending until explicit approval stated |
| Ignoring email chains | Follow entire chain; latest message is authoritative |

## Data Quality Rules

- **Amounts:** Extract as numbers, preserve currency code
- **Dates:** ISO format (YYYY-MM-DD) from email timestamp
- **Status:** Enum only (approved, pending, rejected, processing)
- **Categories:** Use defined taxonomy (see REFERENCE.md for full list)
- **Deduplication:** Same amount + vendor + date = likely duplicate (flag for review)

## Real-World Example

**Input (Email):**
```
From: accounting@company.com
Subject: Invoice AP-12345 Approved
Date: Sep 15, 2026

Hi team,

Invoice AP-12345 from Acme Corp for $5,400.00 (software licenses Q4) 
has been approved for payment.

Amount: $5,400
Due date: Oct 15, 2026
Approver: Sarah Chen
```

**Output (Worklog Entry):**
```json
{
  "activity": "Invoice Approval",
  "amount": 5400,
  "currency": "USD",
  "vendor": "Acme Corp",
  "status": "approved",
  "decision": "Approved for payment - software licenses Q4",
  "owner": "Sarah Chen",
  "date": "2026-09-15",
  "due_date": "2026-10-15",
  "category": "Software",
  "source": "email",
  "source_id": "AP-12345",
  "blockers": null
}
```

## Implementation

See `parser.py` in this directory for working reference implementation.

**Key functions:**
- `extract_activity_type()` - Identify which pattern matches
- `parse_amount()` - Handle currency, decimals, validation
- `extract_vendor()` - Normalize vendor names
- `extract_dates()` - Parse various date formats
- `deduplicate()` - Flag near-duplicates

## Testing Your Parser

Use evals in `evals/` directory:
- `eval-basic-extraction.md` - Simple invoices and approvals
- `eval-edge-cases.md` - Multi-currency, missing data
- `eval-email-chains.md` - Following approval chains
- `eval-deduplication.md` - Catching duplicate transactions

Run with:
```bash
claude eval evals/eval-basic-extraction.md --skill finance-worklog-parser
```
