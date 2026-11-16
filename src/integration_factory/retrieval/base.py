"""Retriever contract. map_schema depends on this, not on any specific database."""
from typing import Protocol

from pydantic import BaseModel


class Record(BaseModel):
    id: str
    text: str            # what gets embedded / BM25-indexed
    metadata: dict = {}  # e.g. vendor, target field, integration name


class Retriever(Protocol):
    def search(self, query: str, k: int = 10) -> list[Record]:
        ...
