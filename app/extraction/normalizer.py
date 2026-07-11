from __future__ import annotations

from typing import Any

AZURE_FIELD_NAME_MAP = {
    "MerchantName": "merchant_name",
    "TransactionDate": "transaction_date",
    "Total": "total",
}


def _field_value(field: dict) -> Any:
    for key, val in field.items():
        if key.startswith("value") and val is not None:
            if isinstance(val, dict) and "amount" in val:
                return val["amount"]
            return val
    return field.get("content")


def _field_source(field: dict) -> dict:
    regions = field.get("boundingRegions") or []
    if not regions:
        return {}
    first = regions[0]
    return {"page": first.get("pageNumber"), "polygon": first.get("polygon")}


def _normalize_azure(raw: dict) -> dict:
    normalized: dict = {}
    documents = raw.get("documents") or []
    if documents:
        for di_name, field in documents[0].get("fields", {}).items():
            name = AZURE_FIELD_NAME_MAP.get(di_name, di_name)
            normalized[name] = {
                "value": _field_value(field),
                "confidence": field.get("confidence"),
                "source": _field_source(field),
            }
    for name, value in raw.get("_custom_fields", {}).items():
        normalized[name] = {"value": value, "confidence": 0.99, "source": {}}
    return normalized


def _normalize_mock(raw: dict) -> dict:
    return {
        name: {"value": data["value"], "confidence": 0.99, "source": {"page": 1}}
        for name, data in raw.get("mock_expected_fields", {}).items()
        if "value" in data
    }

def normalize(raw: dict, provider: str) -> dict:
    return _normalize_azure(raw) if provider == "azure" else _normalize_mock(raw)
