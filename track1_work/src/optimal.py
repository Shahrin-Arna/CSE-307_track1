from __future__ import annotations

from collections import defaultdict, deque
from math import inf
from typing import Sequence

from .metrics import AccessEvent, PolicyRun


def _future_positions(trace: Sequence[int]) -> dict[int, deque[int]]:
    positions: dict[int, deque[int]] = defaultdict(deque)
    for i, page in enumerate(trace):
        positions[page].append(i)
    return positions


def run_optimal(trace: Sequence[int], frame_count: int) -> PolicyRun:
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")

    positions = _future_positions(trace)
    frames: set[int] = set()
    events: list[AccessEvent] = []

    for i, page in enumerate(trace):
        positions[page].popleft()  # consume current access

        if page in frames:
            events.append(AccessEvent(i, page, True, None))
            continue

        evicted = None
        if len(frames) >= frame_count:
            def next_use(p: int) -> float:
                return positions[p][0] if positions[p] else inf

            evicted = max(frames, key=next_use)
            frames.remove(evicted)

        frames.add(page)
        events.append(AccessEvent(i, page, False, evicted))

    return PolicyRun("Optimal", frame_count, events)
