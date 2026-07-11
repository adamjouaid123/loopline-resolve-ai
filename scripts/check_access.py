#!/usr/bin/env python3
"""Independently check access to each configured Azure service.

Each check is isolated in its own try/except: one service failing must not
prevent the others from running, since the point is a per-service breakdown.
"""

from __future__ import annotations

import sys
from typing import Literal

from app.core.config import settings
from app.core.credentials import get_credential

Status = Literal["ok", "fail", "skip"]

def check_foundry() -> tuple[Status, str]:
    if not settings.foundry_project_endpoint:
        return "fail", "FOUNDRY_PROJECT_ENDPOINT is not set"
    try:
        token = get_credential().get_token("https://ai.azure.com/.default")
        return "ok", f"token acquired, expires_on={token.expires_on}"
    except Exception as exc:  # noqa: BLE001 - diagnostic script, we want the raw message
        return "fail", str(exc)

def check_search() -> tuple[Status, str]:
    if not settings.search_endpoint:
        return "fail", "SEARCH_ENDPOINT is not set"
    try:
        from azure.search.documents.indexes import SearchIndexClient

        client = SearchIndexClient(endpoint=settings.search_endpoint, credential=get_credential())
        names = [index.name for index in client.list_indexes()]
        return "ok", f"{len(names)} index(es) visible"
    except Exception as exc:  # noqa: BLE001
        return "fail", str(exc)

def check_storage() -> tuple[Status, str]:
    return "skip", "not yet provisioned — deferred to Phase 4"

CHECKS = {
    "foundry": check_foundry,
    "search": check_search,
    "storage": check_storage,
}


def main() -> int:
    print("=== LoopLine Resolve AI — access check ===")
    any_failed = False
    for name, check in CHECKS.items():
        status, detail = check()
        if status == "fail":
            any_failed = True
        print(f"{name:10s} {status.upper():5s} {detail}")
    return 1 if any_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
