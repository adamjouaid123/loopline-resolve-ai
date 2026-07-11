from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class DocumentProvider(Protocol):
    def analyze(self, path: str, operation: str) -> dict: ...


class SearchProvider(Protocol):
    def search(self, query: str, top_k: int) -> list[dict]: ...


class VisionProvider(Protocol):
    def analyze(self, path: str, schema: dict) -> dict: ...
