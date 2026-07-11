from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class ManifestEntry:
    evidence_id: str
    case_id: str
    original_filename: str
    mime_type: str
    sha256: str
    uploaded_at: str
    synthetic: bool
    provider: str
    storage_uri: str


class Manifest:
    def __init__(self, manifest_path: Path) -> None:
        self.manifest_path = manifest_path
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries = self._load()

    def _load(self) -> list[ManifestEntry]:
        if not self.manifest_path.exists():
            return []
        return [
            ManifestEntry(**json.loads(line))
            for line in self.manifest_path.read_text().splitlines()
            if line.strip()
        ]

    def find_existing(self, case_id: str, sha256: str) -> ManifestEntry | None:
        for entry in self._entries:
            if entry.case_id == case_id and entry.sha256 == sha256:
                return entry
        return None

    def next_evidence_id(self, case_id: str) -> str:
        count = sum(1 for e in self._entries if e.case_id == case_id) + 1
        return f"ev-{case_id}-{count:03d}"

    def append(self, entry: ManifestEntry) -> None:
        self._entries.append(entry)
        with self.manifest_path.open("a") as stream:
            stream.write(json.dumps(asdict(entry)) + "\n")
