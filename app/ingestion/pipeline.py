from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.ingestion.hashing import file_sha256
from app.ingestion.manifest import Manifest, ManifestEntry
from app.ingestion.validators import validate_file


def _paths() -> tuple[Path, Path]:
    root = Path(settings.results_root) / "ingestion"
    return root / "raw", root / "manifest.jsonl"


def ingest_file(source_path: Path, case_id: str, synthetic: bool = True) -> dict:
    raw_root, manifest_path = _paths()
    max_bytes = settings.max_upload_mb * 1024 * 1024

    validated = validate_file(source_path, max_bytes=max_bytes)
    sha256 = file_sha256(validated.path)

    manifest = Manifest(manifest_path)
    existing = manifest.find_existing(case_id, sha256)
    if existing is not None:
        return _to_result(existing)

    dest_dir = raw_root / case_id / sha256
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / source_path.name
    if not dest_path.exists():
        shutil.copy2(validated.path, dest_path)

    entry = ManifestEntry(
        evidence_id=manifest.next_evidence_id(case_id),
        case_id=case_id,
        original_filename=source_path.name,
        mime_type=validated.mime_type,
        sha256=sha256,
        uploaded_at=datetime.now(timezone.utc).isoformat(),
        synthetic=synthetic,
        provider=settings.app_provider_mode,
        storage_uri=f"local://{dest_path.relative_to(Path(settings.results_root))}",
    )
    manifest.append(entry)
    return _to_result(entry)


def _to_result(entry: ManifestEntry) -> dict:
    return {
        "evidence_id": entry.evidence_id,
        "case_id": entry.case_id,
        "sha256": entry.sha256,
        "mime_type": entry.mime_type,
        "storage_uri": entry.storage_uri,
        "immutable": True,
    }
