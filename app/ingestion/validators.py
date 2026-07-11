from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# extension -> (mime_type, header-check function)
SIGNATURES = {
    ".pdf": ("application/pdf", lambda h: h.startswith(b"%PDF")),
    ".png": ("image/png", lambda h: h.startswith(b"\x89PNG\r\n\x1a\n")),
    ".jpg": ("image/jpeg", lambda h: h.startswith(b"\xff\xd8\xff")),
    ".jpeg": ("image/jpeg", lambda h: h.startswith(b"\xff\xd8\xff")),
    ".wav": ("audio/wav", lambda h: h.startswith(b"RIFF") and h[8:12] == b"WAVE"),
    ".mp4": ("video/mp4", lambda h: h[4:8] == b"ftyp"),
    ".json": ("application/json", None),
    ".csv": ("text/csv", None),
    ".txt": ("text/plain", None),
    ".md": ("text/markdown", None),
}

EXECUTABLE_SIGNATURES = (b"MZ", b"\x7fELF", b"#!")


class ValidationError(Exception):
    pass


@dataclass
class ValidatedFile:
    path: Path
    mime_type: str
    size_bytes: int


def validate_file(path: Path, max_bytes: int) -> ValidatedFile:
    if not path.is_file():
        raise ValidationError(f"{path} does not exist")

    size_bytes = path.stat().st_size
    if size_bytes == 0:
        raise ValidationError(f"{path.name} is empty")
    if size_bytes > max_bytes:
        raise ValidationError(f"{path.name} is {size_bytes} bytes, exceeds limit of {max_bytes}")

    extension = path.suffix.lower()
    if extension not in SIGNATURES:
        raise ValidationError(f"{path.name} has unsupported extension '{extension}'")

    header = path.open("rb").read(64)

    if any(header.startswith(sig) for sig in EXECUTABLE_SIGNATURES):
        raise ValidationError(f"{path.name} looks like executable content, rejected")

    mime_type, header_check = SIGNATURES[extension]
    if header_check is not None:
        if not header_check(header):
            raise ValidationError(f"{path.name} content does not match its {extension} extension")
    else:
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"{path.name} claims to be text but is not valid UTF-8") from exc

    return ValidatedFile(path=path, mime_type=mime_type, size_bytes=size_bytes)
