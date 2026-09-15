---
name: mcp-accounting-connector
description: Use when connecting extracted financial data to accounting platforms via MCP (Model Context Protocol) to sync worklog entries to QuickBooks, Wave, or custom accounting APIs
---

# MCP Accounting Connector

## Overview

Sync parsed financial worklog entries to external accounting systems using MCP. Maintains bidirectional communication with accounting platforms—pushing new transactions and pulling account data for reconciliation.

**Core principle:** Parsed data must connect to authoritative financial systems. MCP bridges the gap.

## When to Use

After parsing financial activities (see `finance-worklog-parser` skill), use this to:
- Push new expenses/invoices to QuickBooks, Wave, or custom system
- Pull account balances, reconciliation status
- Link worklog entries to existing transactions
- Check approval workflows in accounting system
- Validate budget allocation before recording

**When NOT to use:** Data that stays in worklog only (don't force everything to accounting software)

## MCP Protocol Basics

**Tool pattern:**
```
mcp::<platform>::<operation>
```

**Example:**
```
mcp::quickbooks::create_invoice
mcp::wave::sync_expense
mcp::custom_api::get_vendor_balance
```

## Supported Platforms

### QuickBooks Online
```
mcp::quickbooks::create_invoice
mcp::quickbooks::update_invoice
mcp::quickbooks::get_account_balance
mcp::quickbooks::list_vendors
```

### Wave Accounting
```
mcp::wave::create_expense
mcp::wave::update_payment_status
mcp::wave::get_customer_balance
mcp::wave::list_invoices
```

### Custom API
```
mcp::custom_api::sync_transaction
mcp::custom_api::validate_budget
mcp::custom_api::get_approval_status
```

## Sync Workflow

### Step 1: Map Worklog Entry to Platform Schema

**Worklog entry:**
```json
{
  "activity": "Invoice Approval",
  "amount": 5400,
  "vendor": "Acme Corp",
  "category": "Software",
  "decision": "Approved for Q4 budget"
}
```

**QuickBooks format:**
```json
{
  "DocNumber": "AP-12345",
  "VendorRef": "acme_corp_id",
  "TxnDate": "2026-09-15",
  "Line": [{
    "Amount": 5400,
    "DetailType": "ExpenseLineDetail",
    "ExpenseLineDetail": {
      "AccountRef": "software_expenses",
      "TaxCodeRef": "tax_exempt"
    }
  }]
}
```

### Step 2: Validate Before Sync

**Checks before sending:**
- [ ] Vendor exists in accounting system (get_vendor_balance)
- [ ] Amount within budget for category
- [ ] Required fields present (don't send incomplete data)
- [ ] No duplicate transaction already exists
- [ ] Currency matches system default

### Step 3: Execute Sync

```
mcp::quickbooks::create_invoice({
  "vendor": "acme_corp_id",
  "amount": 5400,
  "date": "2026-09-15",
  "memo": "Approved for Q4 budget",
  "category": "Software"
})
```

### Step 4: Link and Record

Store response:
```json
{
  "worklog_id": "wl_12345",
  "platform": "quickbooks",
  "platform_id": "inv_98765",
  "sync_date": "2026-09-15T10:30:00Z",
  "status": "synced"
}
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Vendor not found | Look up in MCP, create if authorized |
| Budget exceeded | Flag for approval, don't auto-sync |
| Connection timeout | Retry with exponential backoff |
| Duplicate detected | Link worklog to existing record |
| Permission denied | Check MCP credentials, log attempt |

## Security Patterns

**REQUIRED SUB-SKILL:** Use `safety-hooks` skill to prevent credential leaks.

**Critical checks:**
- Never log API keys or tokens
- Mask sensitive fields in audit trail
- Validate MCP connection before syncing
- Check OAuth scope before operations

## Platform-Specific Guides

### QuickBooks Integration

**Authentication:**
```
mcp::quickbooks::authenticate({
  "oauth_token": "[use Claude CLI credentials]",
  "realm_id": "company_id"
})
```

**Common operations:**
- Create invoice: vendor → worklog entry
- Update payment status: mark as paid
- Get balance: validate vendor creditworthiness

### Wave Integration

**Authentication:**
```
mcp::wave::authenticate({
  "api_key": "[from .env via safety-hooks]",
  "business_id": "business_id"
})
```

**Common operations:**
- Create expense: receipt → accounting record
- List invoices: reconcile worklog against Wave
- Update status: sync approval to Wave

## Real-World Example

**Worklog entry from email:**
```
Activity: Invoice Approval
Amount: $5,400
Vendor: Acme Corp
Status: approved
Category: Software
```

**MCP sync flow:**
```
1. mcp::quickbooks::list_vendors("Acme") 
   → Returns: vendor_id: qb_12345

2. mcp::quickbooks::get_account_balance("Software", "Q4")
   → Returns: budget_remaining: $15,200 ✓ (within budget)

3. mcp::quickbooks::create_invoice({
     vendor: "qb_12345",
     amount: 5400,
     category: "Software",
     memo: "Approved for Q4 budget"
   })
   → Returns: invoice_id: inv_98765, status: "created"

4. Record in worklog:
   platform_sync = {
     platform: "quickbooks",
     platform_id: "inv_98765",
     synced_at: "2026-09-15T10:30:00Z"
   }
```

## Validation Rules

- **Before push:** Validate amount is number, vendor exists, budget available
- **After push:** Confirm platform ID received, status is "created" or "pending"
- **Reconciliation:** Pull from platform monthly, compare against worklog

## Testing Your Connector

See `evals/` directory:
- `eval-quickbooks-sync.md` - Create and update invoices
- `eval-wave-sync.md` - Sync expenses and verify balances
- `eval-error-handling.md` - Budget exceeded, vendor not found
- `eval-deduplication.md` - Don't create duplicate invoices

Run with:
```bash
claude eval evals/eval-quickbooks-sync.md --skill mcp-accounting-connector
```

## Implementation

See `connector.py` in this directory:
- `map_to_platform_schema()` - Convert worklog → platform format
- `validate_before_sync()` - Pre-flight checks
- `create_transaction()` - Execute MCP call
- `record_sync_link()` - Store platform reference

**Required env vars** (set via safety-hooks):
- `QUICKBOOKS_REALM_ID`
- `WAVE_BUSINESS_ID`
- `ACCOUNTING_API_URL` (for custom systems)
