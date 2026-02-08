"""Detect near-duplicate content across scraped resources."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_training_catalog.utils.text_processing import jaccard, trigrams

from .scrapers.base import ScrapedContent


@dataclass
class DuplicateGroup:
    """A group of near-duplicate resources. The first ID is the canonical one."""
    canonical_id: str
    duplicate_ids: list[str] = field(default_factory=list)
    similarity: float = 0.0


class ContentDeduplicator:
    """Identify near-duplicate content using trigram Jaccard similarity.

    Resources with Jaccard similarity above *threshold* are grouped together.
    The resource with the most headings (proxy for depth) is chosen as canonical.
    """

    def __init__(self, threshold: float = 0.85) -> None:
        self._threshold = threshold

    def find_duplicates(self, contents: list[ScrapedContent]) -> list[DuplicateGroup]:
        if len(contents) < 2:
            return []

        # Pre-compute trigram sets
        tri_map: dict[str, set[str]] = {
            c.resource_id: trigrams(c.text_content[:5000])
            for c in contents
        }
        heading_counts: dict[str, int] = {
            c.resource_id: len(c.headings) for c in contents
        }

        # Union-find for grouping
        parent: dict[str, str] = {rid: rid for rid in tri_map}

        def find(x: str) -> str:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: str, b: str) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                # Keep the one with more headings as root
                if heading_counts.get(ra, 0) >= heading_counts.get(rb, 0):
                    parent[rb] = ra
                else:
                    parent[ra] = rb

        ids = list(tri_map.keys())
        pair_sim: dict[tuple[str, str], float] = {}
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                sim = jaccard(tri_map[ids[i]], tri_map[ids[j]])
                if sim >= self._threshold:
                    union(ids[i], ids[j])
                    pair_sim[(ids[i], ids[j])] = sim

        # Build groups
        groups_map: dict[str, list[str]] = {}
        for rid in ids:
            root = find(rid)
            groups_map.setdefault(root, []).append(rid)

        results: list[DuplicateGroup] = []
        for canonical, members in groups_map.items():
            if len(members) < 2:
                continue
            dupes = [m for m in members if m != canonical]
            avg_sim = 0.0
            count = 0
            for d in dupes:
                key = (min(canonical, d), max(canonical, d))
                if key in pair_sim:
                    avg_sim += pair_sim[key]
                    count += 1
            results.append(
                DuplicateGroup(
                    canonical_id=canonical,
                    duplicate_ids=dupes,
                    similarity=avg_sim / count if count else 0.0,
                )
            )

        return results
