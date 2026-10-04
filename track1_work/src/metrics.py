from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class AccessEvent:
    index: int
    page: int
    hit: bool
    evicted: int | None


@dataclass
class PolicyRun:
    policy: str
    frame_count: int
    events: List[AccessEvent]

    def metrics_for_range(self, start: int, end: int, phase: str) -> dict:
        subset = [e for e in self.events if start <= e.index < end]
        accesses = len(subset)
        hits = sum(e.hit for e in subset)
        faults = accesses - hits
        return {
            "policy": self.policy,
            "frames": self.frame_count,
            "phase": phase,
            "accesses": accesses,
            "hits": hits,
            "faults": faults,
            "hit_ratio": hits / accesses if accesses else 0.0,
            "fault_ratio": faults / accesses if accesses else 0.0,
        }

    def before_after_metrics(self) -> list[dict]:
        midpoint = len(self.events) // 2
        return [
            self.metrics_for_range(0, midpoint, "before_shift"),
            self.metrics_for_range(midpoint, len(self.events), "after_shift"),
        ]
