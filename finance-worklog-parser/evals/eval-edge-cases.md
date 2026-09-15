# Eval: Edge Cases & Complex Scenarios

**Purpose:** Verify parser handles real-world complexity—multi-currency, missing data, ambiguous language.

---

## Test Case 1: Multi-Currency Transaction

**Input (Email):**
```
From: international-vendor@europe.com
Subject: Invoice EUR-2026-5678 - Payment Due

Invoice EUR-2026-5678
Amount: €3,500.00 EUR
Equivalent USD: ~$3,850 (at current rates)
Due: October 30, 2026
Vendor: European Software GmbH

Note: Please remit in EUR to our bank account. USD equivalent shown for reference only.
```

**Expected Output:**
```json
{
  "activity": "Invoice Received",
  "amount": 3500,
  "currency": "EUR",
  "amount_usd_equivalent": 3850,
  "vendor": "European Software GmbH",
  "status": "pending",
  "date": "2026-09-15",
  "due_date": "2026-10-30",
  "category": "Software",
  "blockers": "Currency conversion required; verify current exchange rate",
  "note": "Payment must be sent in EUR"
}
```

**Success Criteria:**
- ✓ Amount extracted as 3500 (numeric)
- ✓ Currency identified as EUR
- ✓ USD equivalent noted separately (with flag about rates)
- ✓ Blocker identifies currency complexity
- ✓ Doesn't assume USD

---

## Test Case 2: Missing Critical Information

**Input (Email):**
```
From: someone@unknown-vendor.com
Subject: Your Order Confirmation

Hi there,

Your order has been confirmed. We'll send you an invoice shortly.

Thanks!
```

**Expected Output:**
```json
{
  "activity": "Order Confirmation",
  "amount": null,
  "currency": null,
  "vendor": "unknown-vendor.com",
  "status": "unknown",
  "decision": null,
  "owner": null,
  "date": "2026-09-15",
  "category": null,
  "blockers": "Missing: amount, vendor name, invoice number. Awaiting formal invoice.",
  "next_action": "Wait for invoice email"
}
```

**Success Criteria:**
- ✓ Doesn't invent amount or currency
- ✓ Clearly flags what's missing
- ✓ Extracts what IS available (vendor domain, date)
- ✓ Suggests next action (wait for invoice)
- ✓ Status remains "unknown" (not guessed)

---

## Test Case 3: Email Chain with Multiple Activities

**Input (Email Thread - Most Recent First):**
```
----- MOST RECENT -----
From: payment-team@company.com
Date: September 16, 2026
Subject: RE: Invoice INV-2026-1234

Payment of $2,850.00 has been sent to Acme Corp via ACH.
Reference: INV-2026-1234
Expected arrival: 1-2 business days

----- PREVIOUS -----
From: finance-manager@company.com
Date: September 15, 2026
Subject: RE: Invoice INV-2026-1234

Approved! This invoice for $2,850.00 from Acme Corp has been authorized for immediate payment.

----- ORIGINAL -----
From: supplier@acmecorp.com
Date: September 14, 2026
Subject: Invoice INV-2026-1234

Please find attached invoice for $2,850.00 for software licenses.
```

**Expected Output (Array of 3 entries):**
```json
[
  {
    "activity": "Invoice Received",
    "amount": 2850,
    "vendor": "Acme Corp",
    "status": "pending",
    "date": "2026-09-14",
    "chain_position": 1,
    "chain_id": "thread_inv_2026_1234"
  },
  {
    "activity": "Invoice Approval",
    "amount": 2850,
    "vendor": "Acme Corp",
    "status": "approved",
    "owner": "Finance Manager",
    "date": "2026-09-15",
    "chain_position": 2,
    "chain_id": "thread_inv_2026_1234"
  },
  {
    "activity": "Payment Processed",
    "amount": 2850,
    "vendor": "Acme Corp",
    "status": "paid",
    "owner": "Payment Team",
    "date": "2026-09-16",
    "payment_method": "ACH",
    "chain_position": 3,
    "chain_id": "thread_inv_2026_1234"
  }
]
```

**Success Criteria:**
- ✓ Parses as 3 separate worklog entries (not merged)
- ✓ Each entry has correct status for its stage
- ✓ Maintains chronological order
- ✓ Links entries with chain_id
- ✓ Tracks progression (pending → approved → paid)
- ✓ Uses date from each email, not just the chain date

---

## Test Case 4: Ambiguous Language

**Input (Email):**
```
From: manager@company.com
Subject: Invoice Status Update

The invoice from TechVendor for $5,000 could be approved if we shift some Q4 budget.
We might want to consider this more carefully before committing.
```

**Expected Output:**
```json
{
  "activity": "Invoice Review",
  "amount": 5000,
  "vendor": "TechVendor",
  "status": "pending",
  "decision": null,
  "owner": "Manager",
  "date": "2026-09-15",
  "confidence": "low",
  "uncertainty": [
    "Language is conditional ('could be approved')",
    "No explicit approval given",
    "Budget impact mentioned but not confirmed",
    "Suggests need for further discussion"
  ],
  "blockers": "Awaiting explicit approval decision. Budget impact unclear."
}
```

**Success Criteria:**
- ✓ Status NOT marked as "approved" (could ≠ is)
- ✓ Decision left null (not made yet)
- ✓ Flags ambiguous language
- ✓ Doesn't make assumptions
- ✓ Suggests blocker/next step

---

## Test Case 5: Duplicate Transaction (Same Amount, Vendor, Date)

**Input (Two separate emails):**

**Email 1:**
```
From: accounting@company.com
Subject: Payment Processed - INV-2026-1000

Amount: $1,500.00
Vendor: CloudServices Inc
Date Paid: September 10, 2026
```

**Email 2:**
```
From: accounting-bot@company.com
Subject: Confirmation: Payment to CloudServices

Payment confirmation for $1,500.00 to CloudServices Inc on September 10, 2026.
```

**Expected Output:**
```json
{
  "activity": "Payment Processed",
  "amount": 1500,
  "vendor": "CloudServices Inc",
  "status": "paid",
  "date": "2026-09-10",
  "duplicate_detection": {
    "likely_duplicate": true,
    "reason": "Same amount ($1,500), vendor, and date",
    "confidence": "high",
    "linked_to_entry": "prev_entry_id_12345"
  },
  "recommendation": "Link to existing worklog entry instead of creating new one"
}
```

**Success Criteria:**
- ✓ Identifies likely duplicate
- ✓ Flags for manual review
- ✓ Doesn't auto-delete (user decides)
- ✓ Suggests linking to original

---

## Test Case 6: Partial Information Over Time

**Input (Received in order):**

**Day 1 Email:**
```
From: vendor@techcompany.com
Subject: Invoice #TC-9999

You owe us money. Exact amount TBD based on final headcount.
```

**Day 2 Email:**
```
From: vendor@techcompany.com
Subject: RE: Invoice #TC-9999 - Final Amount

Invoice #TC-9999: $12,500 for consulting services
Due: October 31, 2026
```

**Expected Output - Entry 1 (Day 1):**
```json
{
  "activity": "Invoice Pending Details",
  "amount": null,
  "vendor": "Tech Company",
  "status": "pending",
  "date": "2026-09-14",
  "blockers": "Awaiting final amount"
}
```

**Expected Output - Entry 2 (Day 2):**
```json
{
  "activity": "Invoice Received",
  "amount": 12500,
  "vendor": "Tech Company",
  "status": "pending",
  "date": "2026-09-15",
  "invoice_number": "TC-9999",
  "due_date": "2026-10-31",
  "related_entry": "entry_1",
  "note": "Final amount provided"
}
```

**Success Criteria:**
- ✓ Creates entry even with missing amount (Day 1)
- ✓ Creates new entry when details provided (Day 2)
- ✓ Links entries as related
- ✓ Doesn't try to "update" entries retroactively

---

## RED Phase Baseline

Without skill:
1. Treats multi-currency as error or string
2. Invents data when missing (guesses amount)
3. Merges email chain into single entry
4. Treats "could approve" as approval
5. Misses duplicates entirely
6. Gets confused by partial information

### Rationalizations to Expect

- "I'll just use the first currency I see"
- "The amount must be here somewhere, let me infer it"
- "This is clearly one transaction across three emails"
- "The manager sounds positive, so probably approved"
- "These look different, so must be different transactions"

---

## GREEN Phase Success

With skill:
- ✓ Handles multiple currencies correctly
- ✓ Only uses data explicitly provided
- ✓ Parses email chains into multiple entries
- ✓ Distinguishes "could" from "is"
- ✓ Flags likely duplicates
- ✓ Handles incomplete information gracefully

---

## Running This Eval

```bash
claude eval evals/eval-edge-cases.md --skill finance-worklog-parser
```

**Pass Criteria:**
- Handles multi-currency amounts
- Doesn't invent missing data
- Parses email chains correctly
- Distinguishes conditional from committed language
- Identifies duplicates
- Gracefully handles incomplete information
