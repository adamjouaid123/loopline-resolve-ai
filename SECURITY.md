# Security policy

This is a portfolio/learning project (AI-103 capstone). It uses a synthetic dataset only — no real customer data, credentials, or production systems are involved.

## Reporting a vulnerability

If you find a security issue in this repository, please open a private report via GitHub's "Report a vulnerability" feature on this repo, or contact the maintainer directly, instead of opening a public issue.

## Scope notes

- All sample data under `sample-data/` and `LoopLine-Resolve-AI-Mock-Dataset/` is synthetic; see `manifest/licenses_and_provenance.md` (or `json/provenance.json`) for the no-real-PII declaration.
- Azure credentials are never committed. Local development uses `az login` + `DefaultAzureCredential`; `.env` is git-ignored.
- Any F0/free-tier API keys used as a fallback belong only in a local, untracked `.env` file.
