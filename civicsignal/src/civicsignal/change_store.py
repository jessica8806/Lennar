from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChangeSnapshotStore:
    path: Path

    def load(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {"meetings": {}, "documents": {}}

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        meetings = raw.get("meetings", {})
        documents = raw.get("documents", {})
        return {
            "meetings": {str(key): str(value) for key, value in meetings.items()},
            "documents": {str(key): str(value) for key, value in documents.items()},
        }

    def save(self, meetings: dict[str, str], documents: dict[str, str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "meetings": meetings,
            "documents": documents,
        }
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
