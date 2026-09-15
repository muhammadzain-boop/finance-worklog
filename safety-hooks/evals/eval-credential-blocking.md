# Eval: Pre-Commit Hook Credential Detection

**Purpose:** Verify git pre-commit hooks successfully block commits containing secrets and API credentials.

---

## Test Case 1: API Key Detection

**Scenario:** Developer accidentally stages a config file with API key

**File contents (staged):**
```python
# config.py
QUICKBOOKS_API_KEY = "qb_live_abc123xyz789secret"
WAVE_API_KEY = "wave_live_prod_key_here"
DATABASE_URL = "postgres://admin:password123@db.company.com:5432/finance"
```

**Git Command:**
```bash
git add config.py
git commit -m "Add configuration"
```

**Expected Hook Behavior:**
```
❌ COMMIT BLOCKED

🚨 Pre-commit hook detected sensitive data:

File: config.py
Pattern: API key detected
Line 2: QUICKBOOKS_API_KEY = "qb_live_***"  (secret masked)

Found patterns:
  ✗ Live API key (qb_live_*)
  ✗ Live API key (wave_live_*)
  ✗ Database credentials in connection string

Recommendations:
  1. Remove secrets from config.py
  2. Create .env file (add to .gitignore)
  3. Use environment variables: os.getenv('QUICKBOOKS_API_KEY')
  4. Store secrets in: ~/.env (local machine only)

Run 'git hook list' to see active hooks.
```

**Success Criteria:**
- ✓ Blocks commit immediately
- ✓ Identifies all three secrets
- ✓ Masks sensitive parts in output
- ✓ Suggests safe alternatives
- ✓ Doesn't save/log the secret
- ✓ Shows specific file and line number

---

## Test Case 2: OAuth Token Detection

**Scenario:** Token accidentally included in commit message

**Command:**
```bash
git commit -m "Fix: add authentication token access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
```

**Expected Hook Behavior:**
```
❌ COMMIT BLOCKED

🚨 Pre-commit hook detected sensitive data in commit message:

Pattern: OAuth/Bearer token
Content: "access_token=***"

The commit message contains credentials.

Recommendations:
  1. Remove the token from the commit message
  2. Use git commit --amend to fix message
  3. Don't include secrets in messages ever
  4. For testing, use test tokens only

Commit message should describe WHAT changed, not HOW you authenticated.
```

**Success Criteria:**
- ✓ Scans commit message
- ✓ Blocks if secret found
- ✓ Doesn't save message to history
- ✓ Suggests amending message

---

## Test Case 3: AWS Key Detection

**Scenario:** AWS credentials in environment variable file

**File contents (staged):**
```bash
# .env (about to be committed)
AWS_ACCESS_KEY_ID=AKIA6M2B7XQ5ABCDEFGH
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

**Git Command:**
```bash
git add .env
git commit -m "Add AWS config"
```

**Expected Hook Behavior:**
```
❌ COMMIT BLOCKED

🚨 Critical: .env file is being committed!

File: .env (GITIGNORE VIOLATION)
Pattern: AWS credentials detected (AKIA prefix)

This file contains:
  ✗ AWS access key
  ✗ AWS secret key
  ✗ Would expose production credentials

Actions:
  1. Add .env to .gitignore
  2. Remove from staging: git reset HEAD .env
  3. Keep .env locally ONLY
  4. Use .env.example as template (without real credentials)

Security risk: HIGH
  - AWS keys in git = compromised infrastructure
  - Attackers can spin up expensive resources
  - Credentials are automatically revoked once detected
```

**Success Criteria:**
- ✓ Identifies AWS key format (AKIA prefix)
- ✓ Blocks .env file commit
- ✓ Explains security risk
- ✓ Shows remediation steps
- ✓ High severity alert

---

## Test Case 4: SSN/PII Pattern

**Scenario:** Personal information in CSV test data

**File contents (staged):**
```csv
name,ssn,amount
John Smith,123-45-6789,1500
Jane Doe,987-65-4321,2000
```

**Expected Hook Behavior:**
```
❌ COMMIT BLOCKED

🚨 Pre-commit hook detected PII pattern:

File: test_data.csv
Pattern: Social Security Number (SSN)
Lines: 2-3

Found PII:
  ✗ SSN pattern (123-45-6789)
  ✗ SSN pattern (987-65-4321)

This data should never be in git, even for testing.

Recommendations:
  1. Use anonymized test data
  2. Replace SSN with synthetic values (000-00-0001)
  3. Keep real PII in separate, encrypted database
  4. Never add to version control
```

**Success Criteria:**
- ✓ Detects SSN format
- ✓ Blocks commit
- ✓ Suggests anonymization
- ✓ Explains why (compliance, privacy)

---

## Test Case 5: Safe Commit Passes

**Scenario:** Normal code change (should pass)

**File contents:**
```python
# transaction.py
def process_payment(amount, vendor_id):
    """Process payment using environment variables for credentials."""
    api_key = os.getenv('QUICKBOOKS_API_KEY')
    client = QuickBooks(api_key=api_key)
    return client.create_invoice(amount, vendor_id)
```

**Git Command:**
```bash
git add transaction.py
git commit -m "Add payment processing function"
```

**Expected Hook Behavior:**
```
✓ COMMIT ALLOWED

Pre-commit hook scan passed.
- No API keys found
- No credentials detected  
- No PII patterns matched
- Safe to commit

Committed: transaction.py
```

**Success Criteria:**
- ✓ Passes without blocking
- ✓ Code can be committed
- ✓ Uses environment variables
- ✓ No false positives

---

## Test Case 6: Environment Variable File (gitignored)

**Scenario:** .env file with secrets (should be blocked if staged)

**Hook Configuration:**
```bash
# .gitignore
.env
.env.local
*.key
*.pem
secrets/
```

**When file is staged accidentally:**
```bash
git add .env
```

**Expected Hook Behavior:**
```
❌ COMMIT BLOCKED

⚠️ File pattern violation: .env in .gitignore

This file is configured to be ignored by git but is being staged anyway.

Options:
  1. Don't commit: git reset HEAD .env
  2. Update .gitignore if this file SHOULD be tracked
  3. Create .env.example with placeholder values instead

Files to never commit:
  - .env (local secrets)
  - .env.local (local overrides)
  - *.key, *.pem (private keys)
  - secrets/ (any secrets directory)
```

**Success Criteria:**
- ✓ Blocks .gitignore violations
- ✓ Prevents accidental commits
- ✓ Guides user to alternatives
- ✓ Keeps secrets safe

---

## RED Phase Baseline

Without hook:
1. Secrets get committed to git
2. Exposed in CI/CD logs
3. Visible in git history forever
4. No warning to developer
5. Other team members pull secrets
6. Credentials in backups
7. Risk of unauthorized access

### Rationalizations to Expect

- "It's just a test key"
- "I'll rotate it later"
- "No one has access to this repo"
- "I'll remove it before pushing"
- "Just this once"

---

## GREEN Phase Success

With hook active:
- ✓ Blocks API keys
- ✓ Blocks OAuth tokens
- ✓ Blocks database credentials
- ✓ Blocks PII/SSN patterns
- ✓ Blocks .env file commits
- ✓ Allows safe commits through
- ✓ Provides actionable guidance

---

## REFACTOR Phase: Close Loopholes

**Rationalizations to block:**

1. **"I'll skip the hook":**
   - Hook should be REQUIRED in `.git/config`
   - Can't be skipped with `--no-verify` without explicit permission
   - Document in SECURITY.md why

2. **"I'll amend to remove it":**
   - Amending still leaves secret in git history
   - Need BFG Repo-Cleaner to fully remove
   - Document recovery process

3. **"It's in comments only":**
   - Comments don't matter; secret is still in file
   - Block anyway

4. **"Test environment is safe":**
   - No such thing; secrets can leak from any branch
   - Block all, regardless of branch

5. **"CI/CD needs this secret":**
   - Use CI/CD secrets management (GitHub Secrets, CircleCI, etc.)
   - Never commit to git
   - Document proper flow

---

## Running This Eval

```bash
# Set up test repo
cd /tmp/test-finance-worklog
git init
git config core.hooksPath .git/hooks
cp ~/.claude/skills/safety-hooks/hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

# Run eval
claude eval evals/eval-credential-blocking.md --skill safety-hooks
```

**Pass Criteria:**
- Blocks API keys, tokens, credentials
- Blocks PII patterns
- Blocks .gitignore violations
- Allows clean code through
- Provides clear remediation guidance
- No false negatives (secrets pass through)
- Minimal false positives (clean code blocked)

---

## Integration with Finance Worklog

**REQUIRED before deployment:**

1. Set up hook in repo: `cp hooks/pre-commit .git/hooks/`
2. Test hook with eval above
3. Create .env file (not committed)
4. Create .env.example (template, safe to commit)
5. Document in README how to set up credentials
6. All team members must pass hook test

**Example .env.example (safe to commit):**
```bash
# Copy to .env and fill with real values
QUICKBOOKS_REALM_ID=your_realm_id
QUICKBOOKS_OAUTH_TOKEN=your_token
WAVE_API_KEY=your_api_key
DATABASE_URL=your_db_url
```

**Example setup for new developer:**
```bash
cp .env.example .env
# Edit .env with your credentials
# Never commit .env
```
