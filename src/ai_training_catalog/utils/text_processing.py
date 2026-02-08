"""Text normalisation and similarity utilities."""

from __future__ import annotations

import hashlib
import re
from collections import Counter


def normalise(text: str) -> str:
    """Lower-case, collapse whitespace, strip non-alphanumeric."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def trigrams(text: str) -> set[str]:
    """Return the set of character trigrams in *text*."""
    t = normalise(text)
    return {t[i : i + 3] for i in range(len(t) - 2)} if len(t) >= 3 else {t}


def jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard similarity between two sets."""
    if not a and not b:
        return 1.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def content_hash(text: str) -> str:
    """SHA-256 hex digest of normalised text."""
    return hashlib.sha256(normalise(text).encode()).hexdigest()


def keyword_score(text: str, keywords: list[str]) -> float:
    """Score *text* against a list of *keywords* using simple TF weighting.

    Returns a value between 0.0 and 1.0 indicating relevance.
    """
    words = normalise(text).split()
    word_counts = Counter(words)
    total = sum(word_counts.values()) or 1

    hit_count = 0
    for kw in keywords:
        kw_parts = normalise(kw).split()
        if len(kw_parts) == 1:
            hit_count += word_counts.get(kw_parts[0], 0)
        else:
            # Multi-word keyword: check substring match
            joined = normalise(text)
            kw_joined = " ".join(kw_parts)
            hit_count += joined.count(kw_joined)

    raw = hit_count / total
    # Clamp to [0, 1] — very keyword-dense text scores near 1.0
    return min(raw * 10.0, 1.0)
