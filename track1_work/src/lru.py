from __future__ import annotations

from typing import Sequence

from .metrics import AccessEvent, PolicyRun


def run_lru(trace: Sequence[int], frame_count: int) -> PolicyRun:
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")

    frames: set[int] = set()
    last_used: dict[int, int] = {}
    events: list[AccessEvent] = []

    for i, page in enumerate(trace):
        if page in frames:
            last_used[page] = i
            events.append(AccessEvent(i, page, True, None))
            continue

        evicted = None
        if len(frames) >= frame_count:
            evicted = min(frames, key=lambda p: last_used[p])
            frames.remove(evicted)
            last_used.pop(evicted, None)

        frames.add(page)
        last_used[page] = i
        events.append(AccessEvent(i, page, False, evicted))

    return PolicyRun("LRU", frame_count, events)
