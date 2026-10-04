from __future__ import annotations

from collections import deque
from typing import Sequence

from .metrics import AccessEvent, PolicyRun


def run_fifo(trace: Sequence[int], frame_count: int) -> PolicyRun:
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")

    frames: set[int] = set()
    order: deque[int] = deque()
    events: list[AccessEvent] = []

    for i, page in enumerate(trace):
        if page in frames:
            events.append(AccessEvent(i, page, True, None))
            continue

        evicted = None
        if len(frames) >= frame_count:
            evicted = order.popleft()
            frames.remove(evicted)

        frames.add(page)
        order.append(page)
        events.append(AccessEvent(i, page, False, evicted))

    return PolicyRun("FIFO", frame_count, events)
