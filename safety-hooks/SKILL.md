---
name: safety-hooks
description: Use when handling sensitive financial data (credentials, account numbers, PII) to prevent leaks in logs, transcripts, and worklog entries via pre-commit git hooks
---

# Safety Hooks

## Overview

Implement git hooks that scan staged commits for sensitive financial data before they reach the repository. Catches credential leaks, account numbers, and PII automatically—the last line of defense.

**Core principle:** Prevent secrets from ever entering git history. Hooks are the enforcement mechanism.

## When to Use

**REQUIRED before any finance worklog deployment.**

Use this skill to:
- Block commits containing API keys, OAuth tokens, credentials
- Scan for PII patterns (SSNs, bank accounts, credit card formats)
- Flag likely secrets in commit messages or file contents
- Provide safe alternatives (environment variables, .env, Claude CLI auth)

**Always required:**
- Before first commit of finance worklog code
- When adding new external API integrations
- When any team member joins the project
- When rotating credentials

## Pre-Commit Hook: Credential Detection

**Location:** `.git/hooks/pre-commit`

**Patterns to block:**

| Pattern | Detection | Action |
|---------|-----------|--------|
| API Keys | `api_key=`, `apiKey:`, `APIKEY` | Reject commit |
| OAuth Tokens | `access_token=`, `Bearer ` | Reject commit |
| Database URLs | `postgres://user:pass@`, `mongodb+srv://` | Reject commit |
| AWS Keys | `AKIA` (AWS key prefix), `aws_secret_access_key` | Reject commit |
| Stripe Keys | `sk_live_`, `rk_live_` | Reject commit |
| Private Keys | `-----BEGIN PRIVATE KEY-----` | Reject commit |
| Account Numbers | 16-digit numbers without spaces, IBAN patterns | Reject commit |
| SSN patterns | `\d{3}-\d{2}-\d{4}` or variant | Reject commit |

## Hook Implementation

### Step 1: Enable Hook

```bash
# Copy hook to .git/hooks directory
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Verify it's active
git hook list
```

### Step 2: Configure Patterns

Edit `hooks/pre-commit` to set exclusions:

```bash
# Patterns to scan for
SECRETS_PATTERNS=(
  "api_key"
  "apiKey"
  "access_token"
  "Bearer "
  "AKIA"  # AWS key prefix
  "sk_live_"  # Stripe test key
  "-----BEGIN"  # Private key
  "[0-9]{3}-[0-9]{2}-[0-9]{4}"  # SSN pattern
)

# Files to ignore (false positives)
IGNORE_FILES=(
  "*.md"
  "*.txt"
  "REFERENCE.md"
  "EVALS.md"
)
```

### Step 3: Test the Hook

**Test with a secret (should be rejected):**
```bash
echo "api_key = sk_live_abc123xyz" > test_secret.py
git add test_secret.py
git commit -m "Test commit"  # ❌ Should fail and show warning
```

**Test with safe data (should pass):**
```bash
echo "# This is a safe comment" > test_safe.py
git add test_safe.py
git commit -m "Safe commit"  # ✓ Should succeed
```

## Common Patterns to Protect

### QuickBooks Realm ID
```
# ❌ BAD - exposes sensitive ID
realm_id = "1234567890"

# ✓ GOOD - uses environment variable
realm_id = os.getenv('QUICKBOOKS_REALM_ID')
```

### Wave API Key
```
# ❌ BAD - exposes secret
api_key = "wave_live_abc123xyz789"

# ✓ GOOD - uses environment variable via .env
api_key = os.getenv('WAVE_API_KEY')
```

### Bank Account Numbers in Logs
```
# ❌ BAD - logs contain sensitive data
logger.info(f"Payment to account: {account_number}")

# ✓ GOOD - masks sensitive parts
logger.info(f"Payment to account: {account_number[-4:]}")
```

### Email from Sensitive Contexts
```
# ❌ BAD - includes full email in commit message
git commit -m "Process email from accounting@company.com with SSN 123-45-6789"

# ✓ GOOD - describes activity without exposing data
git commit -m "Process employee expense report"
```

## Environment Variable Pattern

**Create `.env` file (gitignored):**
```bash
# .env (not committed)
QUICKBOOKS_REALM_ID=1234567890
QUICKBOOKS_OAUTH_TOKEN=abc123xyz789
WAVE_API_KEY=wave_live_secret123
DATABASE_URL=postgres://user:pass@host:5432/db
```

**Use in code:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

realm_id = os.getenv('QUICKBOOKS_REALM_ID')
api_key = os.getenv('WAVE_API_KEY')
```

**In `.gitignore`:**
```
.env
.env.local
*.key
*.pem
```

## Accidental Leak Recovery

**If you commit a secret by mistake:**

### Quick Fix (Before Push)
```bash
# Option 1: Amend commit (if not pushed)
git reset --soft HEAD~1
# Remove secret from file
git add .
git commit -m "Fix: remove sensitive data"
```

### Post-Push Fix (Secret Already Exposed)
```bash
# Use git-filter-branch or BFG Repo-Cleaner
# WARNING: This rewrites history

# Install BFG
brew install bfg

# Remove secret from entire history
bfg --delete-files '<(echo "SECRET_VALUE")'

# Force push (only if you own the repo)
git push --force-with-lease
```

## Red Flags: STOP and Check Hooks

If you see ANY of these, interrupt work:
- Committing `.env` file with secrets
- Logging API keys in error messages
- Hardcoding credentials in code
- "Just this once" credentials in commit message
- Uploading private keys as test data

**All of these mean: Don't commit. Clean hooks first.**

## Testing the Hook

Use `test_safety_hooks.sh` in hooks directory:

```bash
./test_safety_hooks.sh
```

Output:
```
✓ Test 1: API key pattern detected
✓ Test 2: OAuth token pattern detected
✓ Test 3: Safe commit passes
✓ Test 4: .env file ignored
All 4 tests passed
```

## Rationalizations to Block

| Excuse | Reality |
|--------|---------|
| "It's just test data" | Test data in git = exposed in CI, backups |
| "I'll rotate it later" | Commits are forever; rotate now or don't commit |
| "It's only local" | Local commits can be pushed by accident |
| "Hook is too strict" | False positives are safe; false negatives are disasters |
| "I'll remove it before push" | Manually removing is error-prone; hooks prevent errors |

**Rule:** If the hook rejects it, the hook is right. Find the safe alternative.

## Hook Configuration Files

**In `hooks/` directory:**
- `pre-commit` - Main hook script (executable)
- `.secretsrc` - Pattern configuration
- `patterns.json` - Detailed regex patterns
- `test_safety_hooks.sh` - Test suite

## Maintenance

**Weekly:**
- Review rejected commits log
- Update patterns if new secret types emerge
- Test hook with team members

**Quarterly:**
- Rotate credentials (API keys, tokens)
- Audit git history for any past leaks
- Update security patterns as tools evolve

## Real-World Failure Case

**What happened:**
- Developer committed `.env` with Wave API key
- CI/CD ran tests, pushed images to registry
- Docker images contain secrets in environment
- Attacker finds images, extracts credentials

**Prevention with safety-hooks:**
- Pre-commit hook blocks `.env` from being committed
- Developer uses environment variable approach instead
- Credentials never enter git history
- Secrets stay safe in CI/CD secrets management

## Integration with MCP Accounting Connector

**REQUIRED:** Before using `mcp-accounting-connector` skill:
1. Enable safety-hooks in your repo
2. Set up .env file with credentials
3. Verify hook rejects secrets
4. Only THEN deploy accounting connector

See `mcp-accounting-connector` skill for credential patterns to protect.

## Implementation

See `hooks/pre-commit` in this directory:
- `scan_staged_files()` - Check what's about to be committed
- `detect_secret_patterns()` - Match against known patterns
- `mask_output()` - Show location without exposing secret
- `safe_alternatives()` - Suggest .env or environment variable fix
