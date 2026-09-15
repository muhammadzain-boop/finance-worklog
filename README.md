# Finance Worklog Skill Bundle

**A complete system for automatically capturing financial activities from communication channels into a structured work log, designed for the Work Log Build Day hackathon.**

This skill bundle implements the pattern established by [worklog-reference](https://github.com/taleemabad-university/worklog-reference), adapted for financial use cases.

---

## 📦 What's Included

This bundle contains three integrated skills, comprehensive evals, and supporting utilities:

### 1. **finance-worklog-parser** 
Extracts structured financial data from unstructured sources (emails, transcripts, Slack).

**What it does:**
- Parses invoice emails → extract amount, vendor, status
- Processes approval chains → track decision path
- Handles meeting transcripts → extract budget discussions
- Deduplicates transactions → prevent duplicate entries
- Gracefully handles missing data → mark unknowns, don't invent

### 2. **mcp-accounting-connector**
Syncs parsed worklog entries to QuickBooks, Wave, or custom accounting APIs via MCP.

**What it does:**
- Maps worklog entries → platform-specific schemas
- Validates budget before syncing → prevents overspend
- Checks for duplicates → prevents duplicate charges
- Looks up vendors → creates new if authorized
- Records sync links → maintains audit trail

### 3. **safety-hooks**
Git pre-commit hooks that block commits containing credentials, API keys, or PII.

**What it does:**
- Blocks API keys and OAuth tokens → prevents credential leaks
- Blocks SSN/PII patterns → protects sensitive data
- Blocks .env files → keeps secrets local only
- Allows safe code through → doesn't impede development
- Provides guidance → suggests .env or environment variables

---

## 🚀 Quick Start

**Read the files in this order:**

1. `finance-worklog-parser/SKILL.md` - Parser skill
2. `mcp-accounting-connector/SKILL.md` - Connector skill
3. `safety-hooks/SKILL.md` - Security skill
4. `SETUP.md` - Installation guide

**Then run the evals to test:**

```bash
claude eval finance-worklog-parser/evals/eval-basic-extraction.md --skill finance-worklog-parser
```

---

## 📂 Directory Structure

```
Nairobi/
├── README.md (you are here)
├── SETUP.md
├── finance-worklog-parser/
│   ├── SKILL.md
│   ├── REFERENCE.md
│   ├── parser.py
│   └── evals/
│       ├── eval-basic-extraction.md
│       └── eval-edge-cases.md
├── mcp-accounting-connector/
│   ├── SKILL.md
│   └── evals/
│       └── eval-quickbooks-sync.md
└── safety-hooks/
    ├── SKILL.md
    └── evals/
        └── eval-credential-blocking.md
```

---

## 🎯 For Hackathon

- **Level 1:** Parser working, basic evals passing
- **Level 2:** MCP connector syncing to accounting system
- **Level 3:** Complete flow with honest evaluation

Start with SETUP.md for step-by-step installation.
