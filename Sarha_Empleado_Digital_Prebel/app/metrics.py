"""100% anonymized aggregate analytics (zero PII, zero phone numbers, zero chat history)."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass, field


def anonymize_session(session_id: str) -> str:
    """Return a short non-reversible anonymous session hash for technical diagnostics."""
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:8]
    return f"anon_{digest}"


@dataclass
class AnonymizedMetrics:
    """In-memory aggregated counters compliant with Ley 1581 de 2012 & Prebel Section 4.5/5.3."""

    total_queries: int = 0
    resolved_queries: int = 0
    out_of_scope_queries: int = 0
    privacy_blocked_events: int = 0
    menu_navigations: int = 0
    by_channel: Counter = field(default_factory=Counter)
    by_category: Counter = field(default_factory=Counter)

    def record_query(
        self,
        channel: str,
        category: str | None,
        is_out_of_scope: bool,
        is_privacy_block: bool = False,
        is_menu: bool = False,
    ) -> None:
        self.total_queries += 1
        self.by_channel[channel] += 1
        if is_privacy_block:
            self.privacy_blocked_events += 1
            return
        if is_out_of_scope:
            self.out_of_scope_queries += 1
            return
        self.resolved_queries += 1
        if is_menu:
            self.menu_navigations += 1
        if category:
            self.by_category[category] += 1

    def snapshot(self) -> dict[str, object]:
        resolved_pct = (
            round((self.resolved_queries / self.total_queries) * 100, 1)
            if self.total_queries
            else 0.0
        )
        return {
            "privacy_guarantee": "Datos 100% anonimizados y agregados; no se almacenan teléfonos, nombres ni historiales de chat.",
            "total_queries": self.total_queries,
            "resolved_queries": self.resolved_queries,
            "out_of_scope_queries": self.out_of_scope_queries,
            "privacy_blocked_events": self.privacy_blocked_events,
            "menu_navigations": self.menu_navigations,
            "resolution_rate_pct": resolved_pct,
            "by_channel": dict(self.by_channel),
            "top_categories": dict(self.by_category.most_common(10)),
        }


metrics = AnonymizedMetrics()
