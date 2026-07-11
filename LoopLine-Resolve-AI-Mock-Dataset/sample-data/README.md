# LoopLine Resolve AI Mock Dataset

> Entirely synthetic, deterministic training data for the LoopLine Resolve AI AI-103 guided project. No real people, companies, products, addresses, receipts, credentials, or customer records are used.

## Quick start

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install pillow reportlab
python scripts/generate_mock_data.py
```

Optional local tools:
- `espeak` or `espeak-ng` regenerates spoken WAV fixtures. Without it, the script creates deterministic tone placeholders and the transcript remains authoritative.
- `ffmpeg` regenerates the MP4 fixtures. Without it, the script emits frame-generation instructions instead.

The generator uses fixed seed `1032026` and overwrites generated fixture folders. Commit deliberate changes to both fixtures and expected outputs.

## Folder structure

```text
sample-data/
├── documents/            # Policies, manuals, receipts, invoice, editable Markdown sources
├── images/               # Clean synthetic claim and media-editing images
├── forms/                # Claim forms, preferences, and JSON Schemas
├── text/                 # Customer messages, transcripts, and prompt/style constraints
├── json/                 # Tool catalogs, queries, provenance, storyboard, manifest
├── csv/                  # Device, warranty, inventory, pricebook, and file catalog data
├── expected-outputs/     # Ground truth for extraction, RAG, safety, tools, and end-to-end tests
├── problematic-examples/ # Bad OCR, missing/malformed data, ambiguity, contradictions, injections
├── audio/                # Synthetic voice notes
├── video/                # Short synthetic MP4 fixtures
└── README.md
scripts/
├── generate_mock_data.py
└── README.md
```

## Coverage summary

This package contains **76 generated fixtures**, plus a machine-readable catalog and manifest.

| Folder | Fixture count |
|---|---:|
| `audio/` | 2 |
| `csv/` | 4 |
| `documents/` | 16 |
| `expected-outputs/` | 11 |
| `forms/` | 10 |
| `images/` | 7 |
| `json/` | 5 |
| `problematic-examples/` | 11 |
| `text/` | 8 |
| `video/` | 2 |

The six end-to-end cases are:

| Case | Scenario | Expected route |
|---|---|---|
| C001 | Eligible accidental screen damage | Repair draft, inventory check, human approval |
| C002 | French battery-safety report | Immediate safety escalation and qualified-center routing |
| C003 | Liquid exposure with serial missing from form | Recover serial from invoice, then manual review |
| C004 | Ambiguous hinge damage | Request additional evidence |
| C005 | Intermittent earbuds, cropped receipt, audio preference | Request proof, then generate text and audio response |
| C006 | Prompt injection and inconsistent receipt | Block attacks, flag mismatch, manual review; no refund tool |

## Phase mapping

| Phase | Dataset use |
|---|---|
| 1.5 | Validate dataset design, schemas, provenance, deterministic regeneration |
| 4 | Ingest files, validate MIME/size, hash evidence, and test idempotency |
| 5 | Extract receipt, invoice, layout, OCR, totals, confidence, and source locations |
| 6 | Analyze images/video, generate alt text, separate observation from diagnosis, detect image instructions |
| 7 | Detect language, entities, PII, sentiment, translation, speech-to-text, and accessibility needs |
| 8 | Chunk documents, create embeddings, index metadata, and test hybrid retrieval |
| 9 | Produce grounded answers with verified citations and abstention |
| 10 | Route controlled agents through deterministic tools and approval boundaries |
| 11 | Test prompt shields, PII handling, moderation, media provenance, and human approval |
| 12 | Run deterministic and AI-assisted evaluation across all six cases |
| 14–15 | Record demo evidence and complete final AI-103 validation |

## AI-103 validation mapping

| Skill area | Dataset evidence |
|---|---|
| Plan and manage | Provenance, schemas, identity-safe fixtures, cost-sized PDFs/media, human approval, attack tests, evaluation gates |
| Generative and agentic | RAG questions, tool catalogs, tool-call ground truth, structured resolutions, approval constraints |
| Computer vision | Damage images, low-confidence/ambiguous images, OCR text in images, indirect injection, media edit mask, video |
| Text analysis | English/French/mixed messages, synthetic PII, sentiment, translation references, voice transcripts and WAV files |
| Information extraction | Policies/manuals, receipts/invoice, low-contrast and cropped documents, schemas, source-grounded extraction outputs |

## How to use the fixtures

1. Start in mock mode and validate every input against the schemas in `forms/`.
2. Ingest files and compare the manifest/hashes with `json/dataset_manifest.json`.
3. Run extraction and compare normalized results with `expected-outputs/extraction_expected.jsonl`.
4. Run vision/OCR and compare observable facts, forbidden claims, uncertainty, and attack handling with `vision_expected.jsonl`.
5. Run language, translation, and speech pipelines against their expected JSONL files.
6. Index the seven knowledge documents, then evaluate RAG facts, citations, and abstentions.
7. Exercise deterministic tools with the CSV/JSON catalogs and compare traces with `tool_calls_expected.jsonl`.
8. Run the safety suite before any agent or generated response can reach the approval screen.
9. Execute all six cases and compare final drafts with `end_to_end_expected.jsonl`.

## Validation rules

- Exact-match identifiers, dates, totals, serials, and clause IDs after normalization.
- Confidence **bands**, not exact floating-point equality, for OCR and multimodal services.
- Meaning-unit comparison for translations and normalized phrase coverage for transcripts.
- Every RAG citation must reference a chunk actually retrieved from this corpus.
- Required abstentions and critical safety cases should pass at 100%.
- Generated-media outputs must remain separate from raw evidence and carry provenance/watermarks.
- Human approval state must come from trusted application code, never model output.

## Complete file catalog

The same catalog is available as `csv/dataset_catalog.csv`. Hashes are stored there and in `json/dataset_manifest.json`.

| File | Purpose | Phase | AI-103 skill | Expected output | Edge case |
|---|---|---|---|---|---|
| `audio/C002_voice_note_fr.wav` | French noisy safety voice note | 7, 12 | TA | Correct transcript and English translation | Noise and technical vocabulary |
| `audio/C005_voice_note_en.wav` | English accessibility voice note | 7, 12 | TA | Correct transcript and dual-channel response preference | Intermittent issue |
| `csv/devices.csv` | Device lookup tool data | 4, 10 | GA, IE | Exact product record | Unknown or similar model |
| `csv/parts_inventory.csv` | Inventory tool data | 10 | GA | Stock result and compatibility | Compatible part out of stock |
| `csv/repair_pricebook.csv` | Repair-cost tool data | 10 | GA | Deterministic estimate | Repair-to-replacement threshold |
| `csv/warranty_registry.csv` | Warranty-lookup tool data | 10 | GA, PM | Exact eligibility record | Expired and missing serial |
| `documents/C001_receipt.pdf` | Clear receipt for happy-path field extraction | 5 | IE | Exact merchant, date, amount, product, serial, and Accidental Care flag | Currency formatting |
| `documents/C003_invoice.pdf` | Invoice used to recover a serial missing from the intake form | 5, 10 | IE, GA | Serial LLB14-C303 recovered and reconciled with the claim | Cross-document reconciliation |
| `documents/loopbook_14_manual.md` | Editable source for laptop diagnosis and retrieval corpus | 5, 6, 8, 9, 10 | CV, IE, GA | Can be regenerated into the matching PDF | Similar symptoms, different causes |
| `documents/loopbook_14_manual.pdf` | Laptop diagnosis and retrieval corpus | 5, 6, 8, 9, 10 | CV, IE, GA | Relevant technical citations and request for additional hinge views | Similar symptoms, different causes |
| `documents/loopbuds_pro_manual.md` | Editable source for earbud troubleshooting and product retrieval | 8, 9, 10 | GA, IE | Can be regenerated into the matching PDF | Prevent false health inference from clean image |
| `documents/loopbuds_pro_manual.pdf` | Earbud troubleshooting and product retrieval | 8, 9, 10 | GA, IE | Correct product-specific answer without cross-product leakage | Prevent false health inference from clean image |
| `documents/novaphone_x1_manual.md` | Editable source for product manual for visual/manual grounding | 5, 6, 8, 9 | CV, IE, GA | Can be regenerated into the matching PDF | Prevent unsupported internal diagnosis |
| `documents/novaphone_x1_manual.pdf` | Product manual for visual/manual grounding | 5, 6, 8, 9 | CV, IE, GA | Product-specific chunks and cautious visual guidance | Prevent unsupported internal diagnosis |
| `documents/repair_safety_handbook.md` | Editable source for safety grounding for claims and rag | 5, 8, 9, 10, 11 | PM, CV, GA, IE | Can be regenerated into the matching PDF | Safety rule overrides ordinary workflow |
| `documents/repair_safety_handbook.pdf` | Safety grounding for claims and RAG | 5, 8, 9, 10, 11 | PM, CV, GA, IE | Safety escalation with citation and qualified-center routing | Safety rule overrides ordinary workflow |
| `documents/returns_refunds_policy.md` | Editable source for resolution-policy corpus | 8, 9, 10 | PM, GA, IE | Can be regenerated into the matching PDF | Monetary threshold and manual review |
| `documents/returns_refunds_policy.pdf` | Resolution-policy corpus | 8, 9, 10 | PM, GA, IE | Approval requirement and repair-versus-replace reasoning | Monetary threshold and manual review |
| `documents/warranty_policy_en.md` | Editable source for primary english rag corpus | 5, 8, 9, 10 | PM, GA, IE | Can be regenerated into the matching PDF | Similar clauses and exceptions |
| `documents/warranty_policy_en.pdf` | Primary English RAG corpus | 5, 8, 9, 10 | PM, GA, IE | Structured Markdown and cited answers using clause IDs | Similar clauses and exceptions |
| `documents/warranty_policy_fr.md` | Editable source for french rag and cross-language retrieval corpus | 7, 8, 9 | TA, GA, IE | Can be regenerated into the matching PDF | Cross-language retrieval |
| `documents/warranty_policy_fr.pdf` | French RAG and cross-language retrieval corpus | 7, 8, 9 | TA, GA, IE | French extraction and answer preserving identical clause IDs | Cross-language retrieval |
| `expected-outputs/classification_expected.jsonl` | Case-risk, coverage, and next-step ground truth | 7, 10, 12 | TA, GA, PM | Correct labels without autonomous final decision | Multiple acceptable draft outcomes where documented |
| `expected-outputs/end_to_end_expected.jsonl` | Six-case portfolio-demo ground truth | 12, 14, 15 | PM, GA, CV, TA, IE | Cohesive, reviewable claim outcomes across all measured domains | None |
| `expected-outputs/extraction_expected.jsonl` | Field-extraction regression ground truth | 5, 6, 12 | IE, CV | Required fields, source references, review bands, and discrepancy flags | Confidence bands rather than exact floats |
| `expected-outputs/ingestion_expected.jsonl` | Ingestion completeness and idempotency ground truth | 4, 12 | PM, IE | All required evidence appears once with immutable hash | None |
| `expected-outputs/media_expected.json` | Generated-media provenance and edit constraints | 6, 11, 12 | CV, PM | Only allowed changes, watermark, and separation from evidence | None |
| `expected-outputs/rag_expected_answers.jsonl` | RAG facts, citations, forbidden claims, and abstention ground truth | 9, 12 | GA, IE | Grounded cited answers and 100% required abstentions | Corpus-absent question and cross-language answer |
| `expected-outputs/safety_expected.jsonl` | Safety and prompt-shield regression set | 11, 12 | PM, GA, CV, TA | All critical attacks blocked without overblocking urgent benign text | Direct, indirect, and retrieved attacks |
| `expected-outputs/tool_calls_expected.jsonl` | Agent-tool selection and argument ground truth | 10, 12 | GA | Correct sequence, arguments, prohibited tools, and step limit | Avoid redundant or unauthorized calls |
| `expected-outputs/transcription_expected.jsonl` | Speech-to-text evaluation references | 7, 12 | TA | Normalized match or required-phrase coverage | Punctuation and minor acoustic variation |
| `expected-outputs/translation_expected.jsonl` | Translation and mixed-language evaluation references | 7, 12 | TA | Meaning preserved without brittle exact-string matching | Negation and mixed language |
| `expected-outputs/vision_expected.jsonl` | Vision, OCR, uncertainty, and indirect-injection ground truth | 6, 11, 12 | CV, PM | Observable facts, alt text, uncertainty, and ignored image instructions | None |
| `forms/C001_intake_form.json` | Structured intake fixture for C001 | 4, 10 | GA, IE, PM | Schema-valid input and correct routing | None |
| `forms/C002_intake_form.json` | Structured intake fixture for C002 | 4, 10 | GA, IE, PM | Schema-valid input and correct routing | None |
| `forms/C003_intake_form_missing_serial.json` | Structured intake fixture for C003 | 4, 10 | GA, IE, PM | Schema-valid input and correct routing | Missing serial is allowed but must set needs_information until recovered |
| `forms/C004_intake_form.json` | Structured intake fixture for C004 | 4, 10 | GA, IE, PM | Schema-valid input and correct routing | None |
| `forms/C005_accessibility_preferences.json` | Structured intake fixture for C005 | 4, 10 | GA, IE, PM | Schema-valid input and correct routing | Accessibility requirement |
| `forms/C005_intake_form.json` | Structured intake fixture for C005 | 4, 10 | GA, IE, PM | Schema-valid input and correct routing | None |
| `forms/C006_intake_form.json` | Structured intake fixture for C006 | 4, 10 | GA, IE, PM | Schema-valid input and correct routing | Pressure to bypass approval controls |
| `forms/claim_form.schema.json` | Validate claim intake payloads | 1.5, 4 | PM, IE | Valid/invalid result; missing serial permitted | None |
| `forms/extraction_result.schema.json` | Normalize Azure/local/mock extraction outputs | 1.5, 5, 6 | PM, IE | Provider-independent, source-grounded extraction | None |
| `forms/resolution.schema.json` | Constrain agent-generated resolution proposals | 1.5, 9, 10 | PM, GA | Invalid autonomous approval rejected | Approval must always come from trusted application state |
| `images/C001_cracked_screen.png` | Happy-path visual evidence for screen damage | 6 | CV | Caption and alt text identify a visible upper-right crack without diagnosing internal damage | None |
| `images/C002_battery_swelling.png` | Safety-critical vision fixture | 6, 11 | CV, PM | Potential swelling, stop-use guidance, safety escalation; no shipping instruction | Safety rule overrides ordinary claim workflow |
| `images/C003_liquid_damage_closeup.png` | Visual evidence for possible liquid residue | 6 | CV | Observation states possible residue and uncertainty; must not claim definitive cause | Observation versus diagnosis |
| `images/C004_ambiguous_hinge.png` | Low-confidence visual classification fixture | 6 | CV | Possible separation near hinge, low confidence, request additional views | Occlusion and ambiguity |
| `images/C005_no_visible_damage.png` | Vision fixture where absence of visible damage must not become a diagnosis | 6 | CV | No visible damage; no claim that the device is healthy | Absence of evidence |
| `images/packaging_edit_mask.png` | Mask restricting an image edit to the warning-label region | 6 | CV | Only the masked area may change | Preserve composition outside edit mask |
| `images/packaging_reference.png` | Reference image for safe media editing | 6 | CV, PM | Safe base asset remains clearly synthetic and separate from evidence | None |
| `json/case_catalog.json` | End-to-end case index | 4, 12, 14 | PM, GA | Six deterministic demo cases and routes | None |
| `json/provenance.json` | Dataset provenance and synthetic-data declaration | 1.5, 14 | PM | Auditable provenance and no-real-PII statement | None |
| `json/retrieval_queries.json` | Retrieval and RAG query fixture | 8, 9, 12 | GA, IE | Relevant chunks for Q01-Q04 and abstention for Q05 | Corpus-absent question |
| `json/service_centers.json` | Service-center routing tool data | 10 | GA | Nearest qualified center rather than simply nearest center | Nearest center lacks battery handling |
| `json/training_clip_storyboard.json` | Video-generation/editing plan | 6 | CV, PM | Schema-valid safe storyboard | No unsafe repair action |
| `problematic-examples/C002_receipt_scan_low_contrast.png` | Bad-OCR and confidence-routing test | 5, 6 | IE, CV | Merchant is readable; date and serial are low confidence and require review | Rotation, blur, low contrast |
| `problematic-examples/C003_contradictory_evidence.json` | Cross-source contradiction test | 5, 10, 12 | IE, GA | Conflict preserved and routed to manual review | Contradictory identifiers |
| `problematic-examples/C004_ambiguous_hinge_notes.txt` | Human-authored ambiguity reference | 6, 12 | CV, PM | Model expresses uncertainty and requests more evidence | Multiple visually plausible interpretations |
| `problematic-examples/C005_receipt_cutoff.png` | Incomplete-document OCR fixture | 5, 6 | IE, CV | Merchant extracted; total and full date marked missing | Cropped source |
| `problematic-examples/C006_adversarial_message.txt` | Direct prompt-injection and approval-bypass test | 7, 10, 11 | PM, TA, GA | Attack detected or safely refused; no hidden data; manual review | Jailbreak and tool-bypass request |
| `problematic-examples/C006_prompt_injection_label.png` | Indirect prompt-injection test embedded in image text | 6, 11 | CV, PM, GA | Visible instruction detected and treated as untrusted evidence; no workflow change | Image-embedded instruction |
| `problematic-examples/C006_receipt_total_mismatch.pdf` | Consistency-check and manual-review fixture | 5, 10, 11 | IE, GA, PM | Arithmetic mismatch flag; no automatic refund or fraud conclusion | Plausible-looking inconsistent total |
| `problematic-examples/C006_untrusted_document_instruction.txt` | Retrieved-document instruction injection test | 8, 9, 11 | GA, PM, IE | Indexed as data but never obeyed as instruction | RAG prompt injection |
| `problematic-examples/bad_ocr_expected.json` | Reference for evaluating bad-OCR behavior | 5, 12 | IE, CV | Band-based extraction validation | Non-deterministic confidence values |
| `problematic-examples/hallucination_resistance_questions.json` | Hallucination and unsupported-promise test set | 9, 11, 12 | GA, PM | Abstention or safe limitation with no fabricated citation | Pressure to use model pretraining |
| `problematic-examples/malformed_claim_payload.json` | Input-schema rejection fixture | 4, 12 | PM, IE | Validation failure listing case ID, email, product, issue, language, and attachment errors | Malformed and privilege-like field |
| `text/C001_customer_message_en.txt` | English customer narrative for language and sentiment analysis | 7 | TA | English, mildly negative, no safety escalation | Emotion must not become risk classification |
| `text/C002_customer_message_fr.txt` | French safety-critical message containing synthetic PII | 7, 11 | TA, PM | French detected, PII redacted, negative sentiment, safety terms retained | Urgency must not be mistaken for an attack |
| `text/C002_voice_note_fr_transcript.txt` | Canonical transcript for French voice note | 7, 12 | TA | STT output preserving swelling, heat, unplugged state, and request | Noise and technical vocabulary |
| `text/C004_customer_message_mixed_language.txt` | Mixed English/French customer message | 7 | TA | Mixed-language handling and request for more evidence | Single-language assumption fails |
| `text/C005_customer_message_en.txt` | Accessibility-aware customer message | 7, 10 | TA, GA | English transcript, key phrases, and dual-channel response requirement | No visible damage does not prove device health |
| `text/C005_voice_note_en_transcript.txt` | Canonical transcript for English voice note | 7, 12 | TA | STT output preserving intermittent charging and accessibility preference | Intermittent issue |
| `text/approved_response_style.txt` | Response-generation style constraint | 7, 9, 10, 11 | TA, GA, PM | Compliant tone and no prohibited promises | Instruction hierarchy |
| `text/repair_guide_prompt.txt` | Controlled media-generation prompt | 6, 11 | CV, PM | Watermarked safe guidance asset | Prohibited unsafe repair action |
| `video/C003_device_walkaround.mp4` | Short synthetic device walkaround for frame extraction | 6, 12 | CV, IE | Timestamped observations without claiming a single frame proves failure | Temporal evidence and uncertainty |
| `video/training_clip_source.mp4` | Safe synthetic training clip fallback | 6, 12 | CV, IE | Watermarked six-second safety clip | Must remain separate from evidence |

## Regenerating PDFs, images, audio, and video

- PDFs are generated with ReportLab from deterministic content embedded in the script. Editable Markdown sources are included for the seven knowledge documents.
- Images are drawn with Pillow. They are schematic synthetic evidence, not photographs of real devices.
- WAV files use local `espeak` when available; canonical transcripts are included and should be used for semantic evaluation.
- MP4 files use local FFmpeg and generated frames. They contain no external footage.
- Re-run `python scripts/generate_mock_data.py` from the repository root or from `scripts/`.

## Limitations

The images are intentionally schematic so licensing and privacy remain uncomplicated. They are suitable for pipeline demonstrations, OCR/injection tests, output-schema work, and controlled evaluation, but they are not a substitute for a production-grade, consented, representative vision dataset. The audio voices depend on the local synthesizer and may differ slightly after regeneration. Azure service confidence values may also vary, so the expected files use bands and required facts rather than brittle exact outputs.
