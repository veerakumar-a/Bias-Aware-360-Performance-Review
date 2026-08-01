from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Dict, List


@dataclass
class DocumentChunk:
    doc_id: str
    source_id: str
    text: str
    metadata: Dict[str, str] = field(default_factory=dict)


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._documents: List[DocumentChunk] = []

    def add_document(self, document: DocumentChunk) -> None:
        self._documents.append(document)

    def clear(self) -> None:
        self._documents.clear()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [token.lower() for token in text.replace("-", " ").split() if token]

    @staticmethod
    def _tfidf_vector(text: str) -> Dict[str, float]:
        tokens = InMemoryVectorStore._tokenize(text)
        total = len(tokens)
        vector: Dict[str, float] = {}
        for token in tokens:
            vector[token] = vector.get(token, 0.0) + 1.0 / total
        return vector

    def search(self, query: str, top_k: int = 5) -> List[tuple[DocumentChunk, float]]:
        query_vector = self._tfidf_vector(query)
        scores: List[tuple[DocumentChunk, float]] = []

        for document in self._documents:
            doc_vector = self._tfidf_vector(document.text)
            overlap = set(query_vector).intersection(doc_vector)
            numerator = sum(query_vector[token] * doc_vector[token] for token in overlap)
            left = sqrt(sum(value * value for value in query_vector.values()))
            right = sqrt(sum(value * value for value in doc_vector.values()))
            denominator = left * right if left and right else 1.0
            similarity = numerator / denominator if denominator else 0.0
            scores.append((document, similarity))

        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]
