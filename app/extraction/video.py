from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from app.extraction.vision import analyze_image


def analyze_video(video_path: str, evidence_id: str, interval_seconds: float = 2.0) -> list[dict]:
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pattern = tmp_path / "frame_%03d.png"
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-vf", f"fps=1/{interval_seconds}", str(pattern)],
            check=True,
            capture_output=True,
        )
        for index, frame_path in enumerate(sorted(tmp_path.glob("frame_*.png"))):
            analysis = analyze_image(str(frame_path), evidence_id=f"{evidence_id}-frame{index:03d}")
            results.append({"timestamp_seconds": index * interval_seconds, **analysis})
    return results
