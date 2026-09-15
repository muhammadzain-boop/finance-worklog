# Finance Worklog - Quick Setup

## Step 1: Copy skills to Claude

```bash
cp -r finance-worklog-parser ~/.claude/skills/
cp -r mcp-accounting-connector ~/.claude/skills/
cp -r safety-hooks ~/.claude/skills/
```

## Step 2: Verify installation

```bash
# List skills
claude skills list | grep finance

# Should show:
# finance-worklog-parser - Use when extracting financial activities...
# mcp-accounting-connector - Use when connecting extracted financial data...
# safety-hooks - Use when handling sensitive financial data...
```

## Step 3: Set up git hooks

```bash
# Copy hook to your repo
cp safety-hooks/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Verify
git hook list
```

## Step 4: Create .env file

```bash
cp .env.example .env  # if available
# Edit .env with your credentials
echo ".env" >> .gitignore
```

## Step 5: Test parser

```bash
cd finance-worklog-parser
python3 parser.py

# Run eval
claude eval evals/eval-basic-extraction.md --skill finance-worklog-parser
```

## Step 6: Test connector

```bash
cd ../mcp-accounting-connector
claude eval evals/eval-quickbooks-sync.md --skill mcp-accounting-connector
```

## Step 7: Test hooks

```bash
cd ../safety-hooks
./hooks/test_safety_hooks.sh

# Should show: All tests passed ✓
```

---

**Done!** All skills are ready to use. Read the individual SKILL.md files for detailed usage.
