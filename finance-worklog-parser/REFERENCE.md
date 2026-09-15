# Finance Worklog Parser - Reference Guide

## Worklog Entry Schema

Complete JSON schema for a finance worklog entry:

```json
{
  "id": "wl_uuid",
  "activity": "string (required)",
  "amount": "number or null",
  "currency": "string (3-letter code) or null",
  "vendor": "string or null",
  "vendor_id": "string or null",
  "status": "enum or null",
  "decision": "string or null",
  "owner": "string or null",
  "date": "ISO 8601 (YYYY-MM-DD)",
  "due_date": "ISO 8601 or null",
  "payment_date": "ISO 8601 or null",
  "category": "enum or null",
  "invoice_number": "string or null",
  "purchase_order_number": "string or null",
  "payment_method": "enum or null",
  "blockers": "string or null",
  "notes": "string or null",
  "source": "enum (email, slack, transcript, upload)",
  "source_id": "string (message ID, file name)",
  "confidence": "enum (high, medium, low)",
  "created_at": "ISO 8601 timestamp",
  "related_entries": ["array of entry IDs"]
}
```

---

## Activity Types

Financial activities that trigger worklog entries:

| Activity | Trigger Pattern | Example |
|----------|-----------------|---------|
| Invoice Received | Invoice arrives | Email with invoice attachment |
| Invoice Approval | Decision to pay | "Approved for payment" |
| Invoice Rejection | Decision not to pay | "Rejected - exceeds budget" |
| Payment Processed | Payment sent | "Payment processed via ACH" |
| Payment Delayed | Payment pending | "Waiting on manager approval" |
| Budget Review | Budget discussion | "Q4 budget planning meeting" |
| Expense Report | Trip/event expenses | "Submitted expense report for conference" |
| Reimbursement | Money paid back to employee | "Reimbursed $500 for travel" |
| Duplicate Alert | Duplicate detected | "This looks like a duplicate of invoice XYZ" |
| Anomaly Alert | Unusual spending | "This vendor's charges are 3x normal" |
| Reconciliation | Matching actual to forecast | "Actual Q3 spending vs forecast" |
| Contract Change | Terms updated | "Vendor contract renewed at lower rate" |

---

## Status Values (Enum)

Allowed values for status field:

```
pending       - Activity initiated, waiting for action
approved      - Decision made to proceed
rejected      - Decision made not to proceed
paid          - Payment sent
received      - Money received (for reimbursements)
unknown       - Status cannot be determined
processing    - In progress (payment being processed)
disputed      - Item in dispute or review
cancelled     - Activity cancelled
on_hold       - Activity paused temporarily
```

---

## Category Taxonomy

Predefined expense categories for consistent reporting:

### Salaries & Compensation
- `salaries` - Regular payroll
- `bonuses` - Performance bonuses
- `benefits` - Health insurance, retirement contributions
- `payroll_taxes` - Employer tax withholding

### Operations
- `office_rent` - Facility lease
- `utilities` - Electricity, water, internet
- `maintenance` - Building/equipment maintenance
- `office_supplies` - Consumables (pens, paper, etc.)
- `equipment` - Computers, furniture

### Technology
- `software` - Licenses, subscriptions (SaaS)
- `cloud_services` - AWS, GCP, Azure
- `hardware` - Servers, networking equipment
- `infrastructure` - Hosting, CDN

### Marketing & Sales
- `marketing` - Advertising, campaigns
- `events` - Conference booths, sponsorships
- `travel` - Air, hotel, ground transportation
- `client_entertainment` - Meals, entertainment

### Professional Services
- `consulting` - External consultant contracts
- `legal` - Legal fees
- `accounting` - Accounting/audit services
- `contractors` - 1099 contractors

### Research & Development
- `research` - Research materials
- `testing` - QA services, tools
- `development` - Third-party dev services

### Other
- `insurance` - General insurance (not benefits)
- `dues_subscriptions` - Memberships, professional dues
- `miscellaneous` - Uncategorized

---

## Currency Codes (ISO 4217)

Common three-letter currency codes:

```
USD - US Dollar
EUR - Euro
GBP - British Pound
JPY - Japanese Yen
CAD - Canadian Dollar
AUD - Australian Dollar
CHF - Swiss Franc
CNY - Chinese Yuan
INR - Indian Rupee
MXN - Mexican Peso
BRL - Brazilian Real
ZAR - South African Rand
```

Full list: https://www.iso.org/iso-4217-currency-codes.html

---

## Payment Methods (Enum)

Allowed values for payment_method:

```
check              - Paper check
ach                - ACH transfer (US bank-to-bank)
wire               - Wire transfer (international)
credit_card        - Credit card charge
debit_card         - Debit card charge
paypal             - PayPal transfer
stripe             - Stripe payment
other              - Payment method not listed
cash               - Cash payment
not_specified      - Not mentioned in source
```

---

## Date Formats

How to handle different date representations:

| Input Format | How to Parse | Output |
|--------------|--------------|--------|
| "Sep 15" | Use email timestamp year | 2026-09-15 |
| "9/15/2026" | MM/DD/YYYY (US format) | 2026-09-15 |
| "15/9/2026" | DD/MM/YYYY (EU format) | 2026-09-15 |
| "2026-09-15" | Already ISO | 2026-09-15 |
| "15 September 2026" | Spelled out | 2026-09-15 |
| "tomorrow" | Relative to email date | email_date + 1 day |
| "next Friday" | Relative to email date | email_date + days to next Friday |

**When uncertain:**
- Use email timestamp as reference point
- Mark confidence as "low"
- Note ambiguity in the entry

---

## Vendor Name Normalization

Extract vendor consistently across variations:

| Variation | Canonical Name |
|-----------|----------------|
| "Acme Corp", "ACME CORP", "acme", "Acme Corporation" | Acme Corp |
| "AWS", "Amazon Web Services" | Amazon Web Services (AWS) |
| "Microsoft", "MSFT", "MS" | Microsoft |
| "Stripe Inc.", "Stripe", "stripe.com" | Stripe |

**Rules:**
1. Use legal name from invoice/company website
2. Consistent capitalization (Title Case)
3. Include "Inc.", "LLC", "Ltd" if on invoice
4. Don't shorten to abbreviations (except well-known: AWS, IBM)
5. Note aliases in `vendor_aliases` field if tracking multiple

---

## Amount Handling

Rules for extracting and storing amounts:

### Basic Amount
- Extract as number (not string): `5400` not `"$5400"`
- No currency symbol in amount field
- Separate currency to `currency` field

### Decimal Places
- Store with up to 2 decimal places: `5400.50`
- Don't invent decimals: `5400` not `5400.00` (both acceptable)

### Tax Handling
- Amount should be subtotal BEFORE tax if tax is itemized
- If only total provided, mark as `amount_includes_tax: true`

### Rounding
- Never round. If invoice says $5,400.47, use 5400.47

### Negative Amounts
- Refunds/credits: Use negative amount: `-500`
- Mark clearly: `transaction_type: "refund"`

### Multi-Line Amounts
- Sum individual items: Item1 ($100) + Item2 ($200) = $300
- List each line item in `line_items` array

---

## Owner Identification

How to extract who owns/approves an activity:

| Pattern | Extract As | Example |
|---------|-----------|---------|
| Email "From:" header | Owner | From: sarah@company.com → Sarah |
| Signature | Owner | "Sincerely, John Smith" → John Smith |
| "Approver:" field | Owner | "Approver: Sarah Chen" → Sarah Chen |
| Meeting attendees | Multiple owners | Sarah, John, Dave |
| "On behalf of X" | Owner | "On behalf of Finance Director" → Finance Director |
| Job title only | Owner | "Finance Manager" → Finance Manager (if name missing) |

**When uncertain:**
- Leave blank or use "Unknown"
- Don't guess person's name

---

## Confidence Levels

Mark confidence when data quality is uncertain:

```
high    - Clear, explicit, from authoritative source
medium  - Reasonably clear, some interpretation needed
low     - Ambiguous, inferred, or incomplete
```

### Examples

**High confidence:**
- Invoice with all line items and totals
- Email with explicit approval

**Medium confidence:**
- Email mentioning amount in prose (not itemized)
- Vendor name inferred from email domain
- Activity type inferred from subject line

**Low confidence:**
- Conditional approval ("might approve")
- Ambiguous amounts ("around $5,000")
- Vendor name spelled multiple ways in same email

---

## Red Flags & Indicators

Watch for these patterns when parsing:

| Flag | Meaning | Action |
|------|---------|--------|
| Multiple currencies | International transaction | Note equivalent amounts |
| Large jump in amount | Possible typo | Flag for verification |
| No vendor name | Suspicious | Mark blocker: "missing vendor" |
| Conditional language | Not finalized | Status remains "pending" |
| Multiple amounts | Confusing | List all with source |
| Email chain | Multiple activities | Parse as separate entries |
| Date missing | Unclear timing | Use email timestamp |
| Duplicate amount+vendor+date | Likely duplicate | Flag for deduplication |
| Unusual category | Might misclassify | Mark low confidence |

---

## Common Extraction Patterns

### Pattern: Approval Email
```
Keywords: approved, authorized, proceed, okay, confirmed
Structure: "Invoice [X] for $[amount] from [vendor] has been approved"
Extract: activity=Invoice Approval, status=approved, decision=reason
```

### Pattern: Rejection Email
```
Keywords: rejected, denied, declined, cannot approve, hold
Structure: "Invoice rejected because [reason]"
Extract: activity=Invoice Rejection, status=rejected, blockers=reason
```

### Pattern: Meeting Discussion
```
Keywords: discussed, reviewed, debated, planning, forecast
Structure: Unstructured meeting notes mentioning budget/spending
Extract: activity=Budget Review, amounts from notes, decisions if made
```

### Pattern: Expense Report
```
Keywords: submitted, expense, reimbursement, receipt
Structure: "I spent $X on Y for Z event"
Extract: activity=Expense Report, amount=X, category=inferred from Y
```

---

## Data Quality Checklist

Before finalizing an entry:

- [ ] Amount is numeric (not string)
- [ ] Currency is valid ISO 4217 code
- [ ] Date is ISO 8601 format
- [ ] Status is from enum (not free text)
- [ ] Category is from taxonomy (if provided)
- [ ] Vendor name is consistent/normalized
- [ ] Owner is extracted from source (not guessed)
- [ ] No invented fields
- [ ] Confidence level assigned
- [ ] Blockers clearly stated
- [ ] Source and source_id recorded

---

## Validation Rules

Before accepting an entry, verify:

```
✓ activity: one of Activity Types list
✓ amount: null OR positive number
✓ currency: null OR valid ISO 4217 code
✓ vendor: null OR non-empty string
✓ status: null OR from Status enum
✓ date: valid ISO 8601 date
✓ due_date: null OR valid ISO 8601 date
✓ category: null OR from Category Taxonomy
✓ owner: null OR non-empty string
✓ confidence: high, medium, or low
```

If any validation fails:
1. Flag the entry
2. Don't discard data
3. Mark affected field with `validation_error: reason`
4. Move entry to "review" queue

---

## Examples: End to End

### Example 1: Simple Invoice

**Raw Input:**
```
Invoice #INV123 from ACME for $5,000 due Oct 31
```

**Parsed Entry:**
```json
{
  "activity": "Invoice Received",
  "amount": 5000,
  "currency": "USD",
  "vendor": "Acme Corp",
  "status": "pending",
  "date": "2026-09-15",
  "due_date": "2026-10-31",
  "invoice_number": "INV123",
  "confidence": "high"
}
```

### Example 2: Complex Approval Chain

**Raw Input (Email thread):**
```
1. Vendor sends invoice for $12,500 consulting
2. Manager approves "Let's move forward"
3. Finance lead approves "Budget is available"
4. Accounting confirms "Payment submitted"
```

**Parsed Entries (3):**
```json
{
  "activity": "Invoice Received",
  "amount": 12500,
  "vendor": "Consulting Firm",
  "status": "pending"
}
{
  "activity": "Invoice Approval",
  "amount": 12500,
  "vendor": "Consulting Firm",
  "status": "approved",
  "owner": "Manager",
  "decision": "Approved to move forward"
}
{
  "activity": "Payment Processed",
  "amount": 12500,
  "vendor": "Consulting Firm",
  "status": "paid",
  "owner": "Accounting"
}
```

---

## Troubleshooting

**Problem: Can't determine vendor name**
- Solution: Use email domain or "Unknown" with blocker

**Problem: Multiple amounts mentioned**
- Solution: Extract all, mark ambiguous, flag for review

**Problem: Conditional approval ("should approve")**
- Solution: Status stays "pending", don't mark as approved

**Problem: Email chain with multiple activities**
- Solution: Parse as array of separate entries

**Problem: Missing due date**
- Solution: Leave null, don't invent

**Problem: Currency not specified**
- Solution: Assume USD, mark low confidence, flag for verification

