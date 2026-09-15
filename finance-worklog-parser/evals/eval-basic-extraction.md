# Eval: Basic Financial Activity Extraction

**Purpose:** Verify the parser correctly extracts simple financial activities from emails.

**RED Phase (Baseline without skill):** Agent should struggle to identify what data to extract and may guess at field names or miss structured output.

## Test Case 1: Simple Invoice Email

**Input (Email):**
```
From: supplier@acmecorp.com
Subject: Invoice #INV-2026-1234
Date: September 15, 2026, 2:30 PM

Hi there,

Please find attached our invoice for the software licenses ordered in August.

Invoice Number: INV-2026-1234
Amount: $2,850.00
Due Date: October 15, 2026
Description: 10 licenses of SoftwareXYZ for one year

Best regards,
Acme Corp Accounting
```

**Expected Output:**
```json
{
  "activity": "Invoice Received",
  "amount": 2850,
  "currency": "USD",
  "vendor": "Acme Corp",
  "status": "pending",
  "decision": null,
  "owner": "Accounts Payable",
  "date": "2026-09-15",
  "due_date": "2026-10-15",
  "category": "Software",
  "invoice_number": "INV-2026-1234",
  "blockers": null
}
```

**Success Criteria:**
- ✓ Amount extracted as 2850 (number)
- ✓ Currency identified as USD
- ✓ Vendor name extracted as "Acme Corp"
- ✓ Status marked as "pending" (not approved yet)
- ✓ Category inferred as "Software"
- ✓ Due date extracted in ISO format

---

## Test Case 2: Approval Decision Email

**Input (Email):**
```
From: manager@company.com
To: accounting@company.com
Subject: APPROVED: Invoice INV-2026-1234

Invoice INV-2026-1234 from Acme Corp for $2,850.00 has been reviewed and approved for payment.

Reason: Essential software licenses for the engineering team
Budget: Q3 Software Budget
Approver: Sarah Chen, Finance Manager
```

**Expected Output:**
```json
{
  "activity": "Invoice Approval",
  "amount": 2850,
  "currency": "USD",
  "vendor": "Acme Corp",
  "status": "approved",
  "decision": "Approved for payment - essential software licenses",
  "owner": "Sarah Chen",
  "date": "2026-09-15",
  "category": "Software",
  "invoice_number": "INV-2026-1234",
  "blockers": null
}
```

**Success Criteria:**
- ✓ Status correctly identified as "approved"
- ✓ Decision captured with reason
- ✓ Owner extracted as "Sarah Chen"
- ✓ Amount and vendor correctly linked to same invoice

---

## Test Case 3: Rejection with Reason

**Input (Email):**
```
From: finance-lead@company.com
Subject: RE: Invoice INV-2026-1235 - REJECTED

This invoice has been rejected.

Reason: Amount exceeds approved vendor contract limit by $500
Action required: Renegotiate with vendor or request special approval
Contact: David Martinez (Finance Lead) to discuss options

Due for resubmission: within 5 business days
```

**Expected Output:**
```json
{
  "activity": "Invoice Rejection",
  "amount": null,
  "vendor": null,
  "status": "rejected",
  "decision": "Rejected - exceeds vendor contract limit by $500",
  "owner": "David Martinez",
  "date": "2026-09-15",
  "category": null,
  "blockers": "Renegotiate vendor contract or request special approval. Resubmit within 5 business days.",
  "next_steps": "Contact David Martinez"
}
```

**Success Criteria:**
- ✓ Status correctly identified as "rejected"
- ✓ Reason captured in decision
- ✓ Blocker clearly stated
- ✓ Doesn't invent fields not provided (amount, vendor, category are null)

---

## Test Case 4: Payment Processing Notification

**Input (Email):**
```
From: accounting-bot@company.com
Subject: Payment Processed - Invoice INV-2026-1234

Payment confirmation:
Amount: $2,850.00
Vendor: Acme Corp
Date Paid: September 16, 2026
Payment Method: ACH Transfer
Check Number: N/A
Reference: INV-2026-1234
```

**Expected Output:**
```json
{
  "activity": "Payment Processed",
  "amount": 2850,
  "currency": "USD",
  "vendor": "Acme Corp",
  "status": "paid",
  "decision": "Payment sent via ACH transfer",
  "owner": "Accounting",
  "date": "2026-09-16",
  "payment_method": "ACH",
  "invoice_number": "INV-2026-1234",
  "blockers": null
}
```

**Success Criteria:**
- ✓ Status identified as "paid"
- ✓ Payment method extracted
- ✓ Date marked as payment date, not invoice date
- ✓ Transaction linked to original invoice

---

## RED Phase Baseline

Without the skill, the agent likely:
1. Extracts all text without structure
2. Uses inconsistent field names ("amount_paid" vs "amount", "vendor_name" vs "vendor")
3. Includes too much raw text instead of extracting key fields
4. Misses date parsing (returns "September 15" instead of "2026-09-15")
5. Treats approval and rejection the same way
6. Invents fields not in the source ("reason" instead of "decision")

### Rationalizations to Expect

- "The email is somewhat clear, so I'll just pass it through as-is"
- "All this data could be useful, better include everything"
- "Status field isn't explicitly stated so I won't include it"
- "Amount includes currency, so I'll keep it as string '$2,850.00'"
- "I don't know what category this is, so I won't include category field"

---

## GREEN Phase Success

With the skill applied, the agent should:
1. ✓ Extract only structured fields
2. ✓ Use consistent field naming
3. ✓ Parse dates to ISO format
4. ✓ Distinguish between invoice states (pending → approved → paid)
5. ✓ Only include fields present in source (null for missing)
6. ✓ Mark unclear fields as "unknown" or null (not invent)

---

## REFACTOR Phase: Close Loopholes

**Common second-round mistakes to catch:**

1. **Ambiguous approval language:**
   - Input: "We should probably approve this"
   - Wrong: marks as "approved"
   - Right: marks as "pending" (should ≠ approved)

2. **Multi-recipient emails:**
   - Input: Email to multiple people including "Sarah Chen"
   - Wrong: marks only first recipient as owner
   - Right: uses approver's name when stated ("Approver: Sarah Chen")

3. **Amounts with typos:**
   - Input: "$2,850.00" but text says "2,850.00" 
   - Wrong: parses as inconsistent
   - Right: normalizes to single numeric value

4. **Partial vendor names:**
   - Input: "Acme" in text, but "Acme Corp" in signature
   - Wrong: creates two separate vendor entries
   - Right: uses full legal name from subject line or signature

5. **Date ambiguity:**
   - Input: "Sep 15" without year
   - Wrong: returns "Sep 15" as string
   - Right: uses email date context to determine year

---

## Running This Eval

```bash
# Test the parser skill
claude eval evals/eval-basic-extraction.md --skill finance-worklog-parser

# Expected output: All 4 test cases pass with structured JSON output
```

**Pass Criteria:**
- All fields correctly extracted
- No invented data
- Consistent formatting
- ISO date format
- Enum status values only
