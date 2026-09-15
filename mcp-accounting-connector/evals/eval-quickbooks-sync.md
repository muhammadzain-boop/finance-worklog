# Eval: QuickBooks Sync Integration

**Purpose:** Verify MCP connector correctly syncs parsed worklog entries to QuickBooks without data loss or corruption.

---

## Test Case 1: Simple Invoice Creation

**Input (Parsed Worklog Entry):**
```json
{
  "activity": "Invoice Received",
  "amount": 2850,
  "currency": "USD",
  "vendor": "Acme Corp",
  "status": "pending",
  "date": "2026-09-15",
  "due_date": "2026-10-31",
  "invoice_number": "INV-2026-1234",
  "category": "Software"
}
```

**MCP Call Expected:**
```
mcp::quickbooks::create_invoice({
  "vendor_ref": "acme_corp_id",  // Looked up via list_vendors
  "amount": 2850,
  "date": "2026-09-15",
  "due_date": "2026-10-31",
  "description": "Software license",
  "category_ref": "software_expenses",
  "memo": "INV-2026-1234"
})
```

**Expected Response:**
```json
{
  "status": "success",
  "platform_id": "qb_invoice_98765",
  "amount_created": 2850,
  "vendor": "acme_corp_id",
  "date_created": "2026-09-15T10:30:00Z"
}
```

**Worklog Link Update:**
```json
{
  "platform_sync": {
    "platform": "quickbooks",
    "platform_id": "qb_invoice_98765",
    "synced_at": "2026-09-15T10:30:00Z",
    "status": "synced"
  }
}
```

**Success Criteria:**
- ✓ Vendor looked up successfully
- ✓ Amount transferred exactly (no rounding)
- ✓ Category mapped correctly
- ✓ Platform ID stored in worklog
- ✓ Sync timestamp recorded

---

## Test Case 2: Budget Validation Before Sync

**Input (Parsed Entry):**
```json
{
  "amount": 15000,
  "vendor": "BigVendor Inc",
  "category": "Equipment",
  "decision": "Approved"
}
```

**Sync Workflow:**
```
1. Call mcp::quickbooks::get_account_balance("Equipment", "2026Q4")
2. Response: { "budget_available": 5000, "amount_allocated": 10000 }
3. Check: 15000 > 5000 (remaining budget)
4. Result: BLOCKED - Budget exceeded
```

**Expected Output (No sync):**
```json
{
  "status": "blocked",
  "reason": "Budget exceeded",
  "details": {
    "requested_amount": 15000,
    "budget_available": 5000,
    "budget_allocated": 10000,
    "budget_total": 15000,
    "deficit": 10000
  },
  "action": "Flag for manual approval or budget reallocation"
}
```

**Success Criteria:**
- ✓ Does NOT create transaction automatically
- ✓ Flags for review
- ✓ Shows budget gap clearly
- ✓ Suggests action (manual approval)

---

## Test Case 3: Vendor Not Found

**Input:**
```json
{
  "amount": 5000,
  "vendor": "NewUnknownVendor LLC",
  "status": "approved"
}
```

**Sync Workflow:**
```
1. Call mcp::quickbooks::list_vendors("NewUnknownVendor")
2. Response: { "vendors": [] }  // Not found
3. Check: Can we create new vendor?
4. Result: Check permissions
```

**Expected Output (With permission check):**
```json
{
  "status": "pending_vendor_setup",
  "reason": "Vendor not found in QuickBooks",
  "vendor": "NewUnknownVendor LLC",
  "options": [
    {
      "action": "create_vendor",
      "permission_required": "vendor_create",
      "status": "authorized"
    },
    {
      "action": "skip_sync",
      "reason": "Wait for manual vendor setup"
    }
  ],
  "recommendation": "Create vendor and retry sync"
}
```

**Success Criteria:**
- ✓ Detects missing vendor
- ✓ Doesn't invent vendor
- ✓ Checks permissions before creating
- ✓ Offers options to user

---

## Test Case 4: Duplicate Detection

**Input (Two separate worklog entries, same data):**
```json
{
  "amount": 1500,
  "vendor": "CloudServices Inc",
  "date": "2026-09-10",
  "invoice_number": "CS-5678"
}
```

**Sync Workflow:**
```
1. Call mcp::quickbooks::list_invoices({
     vendor: "CloudServices Inc",
     amount: 1500,
     date: "2026-09-10"
   })
2. Response: { "matches": [{ id: "qb_99999", amount: 1500 }] }
3. Check: Exact match found
4. Result: Link to existing, don't create new
```

**Expected Output:**
```json
{
  "status": "linked_existing",
  "existing_transaction": {
    "platform_id": "qb_99999",
    "amount": 1500,
    "date": "2026-09-10",
    "vendor": "CloudServices Inc"
  },
  "action": "Linked worklog entry to existing QuickBooks transaction"
}
```

**Success Criteria:**
- ✓ Detects duplicate
- ✓ Links instead of creates
- ✓ No duplicate charges
- ✓ Maintains data integrity

---

## Test Case 5: Approved Transaction Sync

**Input (Status = approved, ready to pay):**
```json
{
  "amount": 5400,
  "vendor": "Acme Corp",
  "status": "approved",
  "decision": "Approved for Q4 budget",
  "date": "2026-09-15"
}
```

**Sync Workflow:**
```
1. Check status: "approved" → Proceed to sync
2. Call mcp::quickbooks::create_invoice(...)
3. Success response received
4. Call mcp::quickbooks::mark_approved(...) // Optional
```

**Expected Output:**
```json
{
  "status": "synced",
  "platform_id": "qb_invoice_12345",
  "approval_status": "approved_in_quickbooks",
  "next_step": "Awaiting payment"
}
```

**Success Criteria:**
- ✓ Only syncs when status is "approved"
- ✓ Doesn't sync "pending" or "rejected"
- ✓ Records approval status

---

## RED Phase Baseline

Without skill:
1. Syncs without validating budget
2. Creates duplicate transactions
3. Can't find vendors, fails silently
4. Doesn't check approval status
5. Creates transaction with wrong amount
6. Loses sync tracking (no platform_id)

### Rationalizations to Expect

- "The amount looks right, just sync it"
- "Vendor not found? Just use the name directly"
- "I'll sync everything and let accounting sort it out"
- "Status is kind of approved, might as well create it"

---

## GREEN Phase Success

With skill:
- ✓ Validates budget before sync
- ✓ Checks for duplicates
- ✓ Verifies vendor exists (or creates with permission)
- ✓ Only syncs when status is approved
- ✓ Verifies amount matches source
- ✓ Records platform_id for reconciliation

---

## REFACTOR Phase: Close Loopholes

**Common failures to catch:**

1. **Rounding errors:**
   - Input: $2,850.49
   - Wrong: Syncs as 2850.50 (rounded)
   - Right: Syncs as 2850.49 (exact)

2. **Currency mismatch:**
   - Input: Amount in EUR, QB in USD
   - Wrong: Syncs without conversion
   - Right: Converts or flags for review

3. **Vendor name variations:**
   - Input: "Acme" in worklog, "Acme Corp" in QB
   - Wrong: Creates duplicate vendor entry
   - Right: Matches on normalized name

4. **Status ambiguity:**
   - Input: Status is "processing"
   - Wrong: Syncs as if approved
   - Right: Waits for "approved" or "paid"

5. **Half-synced state:**
   - Input: Platform returns error after partial update
   - Wrong: Leaves worklog out of sync
   - Right: Rolls back or marks as "sync_failed"

---

## Running This Eval

```bash
claude eval evals/eval-quickbooks-sync.md --skill mcp-accounting-connector
```

**Pass Criteria:**
- Validates budget before sync
- Detects duplicates
- Handles missing vendors gracefully
- Respects approval status
- Maintains sync integrity
- No data loss or corruption
