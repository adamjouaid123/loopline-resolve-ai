# Mock-data generator

`generate_mock_data.py` deterministically rebuilds the complete LoopLine Resolve AI fixture package.

## Requirements

- Python 3.11 or newer
- Pillow
- ReportLab
- Optional: `espeak` or `espeak-ng` for spoken WAV fixtures
- Optional: FFmpeg for MP4 fixtures

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install pillow reportlab
python scripts/generate_mock_data.py
```

The script uses fixed seed `1032026`, deletes and recreates generated fixture folders, and writes:

- PDF and Markdown knowledge documents
- receipts and invoices
- synthetic images and OCR edge cases
- claim forms and JSON Schemas
- CSV/JSON tool catalogs
- customer text and transcripts
- WAV voice notes when a local synthesizer is available
- MP4 fixtures when FFmpeg is available
- deterministic expected-output JSONL files
- `sample-data/csv/dataset_catalog.csv`
- `sample-data/json/dataset_manifest.json`
- `sample-data/README.md`

No internet access or external assets are required. All content is fictional.
