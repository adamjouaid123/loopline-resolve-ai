from __future__ import annotations

import re

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

from app.core.config import settings

OPERATION_TO_MODEL = {
    "layout": "prebuilt-layout",
    "receipt": "prebuilt-receipt",
    "invoice": "prebuilt-invoice",
    "read": "prebuilt-read",
}

SERIAL_PATTERN = re.compile(r"Serial[:\s]+([A-Z0-9]{2,10}-[A-Z0-9]{2,10})", re.IGNORECASE)
ACCIDENTAL_CARE_PATTERN = re.compile(r"accidental\s*(care|damage)", re.IGNORECASE)
CALCULATED_TOTAL_PATTERN = re.compile(r"Calculated total\s*EUR\s*([\d.]+)", re.IGNORECASE)
PRINTED_TOTAL_PATTERN = re.compile(r"Printed total\s*EUR\s*([\d.]+)", re.IGNORECASE)


def _client() -> DocumentIntelligenceClient:
    credential = (
        AzureKeyCredential(settings.document_intelligence_key)
        if settings.document_intelligence_key
        else DefaultAzureCredential()
    )
    return DocumentIntelligenceClient(endpoint=settings.document_intelligence_endpoint, credential=credential)


def analyze(path: str, operation: str) -> dict:
    model_id = OPERATION_TO_MODEL[operation]
    client = _client()
    with open(path, "rb") as source:
        poller = client.begin_analyze_document(model_id, body=source)
    raw = poller.result().as_dict()
    raw["_custom_fields"] = _extract_custom_fields(raw.get("content", ""))
    return raw


def _extract_custom_fields(content: str) -> dict:
    custom: dict = {}

    serial_match = SERIAL_PATTERN.search(content)
    if serial_match:
        custom["serial_number"] = serial_match.group(1)

    if ACCIDENTAL_CARE_PATTERN.search(content):
        custom["accidental_care"] = True

    calc_match = CALCULATED_TOTAL_PATTERN.search(content)
    printed_match = PRINTED_TOTAL_PATTERN.search(content)
    if calc_match and printed_match:
        line_items_total = float(calc_match.group(1))
        printed_total = float(printed_match.group(1))
        custom["line_items_total"] = line_items_total
        custom["printed_total"] = printed_total
        custom["arithmetic_mismatch"] = line_items_total != printed_total

    return custom
