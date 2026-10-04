from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from math import inf
from typing import Sequence

import numpy as np
from sklearn.tree import DecisionTreeClassifier

from .metrics import AccessEvent, PolicyRun


@dataclass
class LearnedModel:
    classifier: DecisionTreeClassifier

    def score_candidates(self, features: list[list[float]]) -> np.ndarray:
        """Return probability that each candidate is a good page to evict."""
        if hasattr(self.classifier, "predict_proba"):
            proba = self.classifier.predict_proba(features)
            classes = list(self.classifier.classes_)
            if 1 in classes:
                return proba[:, classes.index(1)]
        return self.classifier.predict(features).astype(float)


def _candidate_features(page: int, current_index: int,
                        last_seen: dict[int, int],
                        frequency: Counter[int]) -> list[float]:
    # Larger recency means the page has not been used for longer.
    recency = current_index - last_seen.get(page, -1)
    freq = frequency.get(page, 0)
    return [float(recency), float(freq)]


def build_training_data(trace: Sequence[int], frame_count: int) -> tuple[np.ndarray, np.ndarray]:
    """Create candidate-level examples using Optimal decisions as labels.

    Each time memory is full and a fault occurs, every resident page becomes a
    training example. The page that Optimal would evict receives label 1; the
    other resident pages receive label 0.
    """
    positions: dict[int, deque[int]] = defaultdict(deque)
    for i, page in enumerate(trace):
        positions[page].append(i)

    frames: set[int] = set()
    last_seen: dict[int, int] = {}
    frequency: Counter[int] = Counter()
    X: list[list[float]] = []
    y: list[int] = []

    for i, page in enumerate(trace):
        positions[page].popleft()
        frequency[page] += 1

        if page in frames:
            last_seen[page] = i
            continue

        if len(frames) >= frame_count:
            def next_use(p: int) -> float:
                return positions[p][0] if positions[p] else inf

            optimal_victim = max(frames, key=next_use)
            for candidate in sorted(frames):
                X.append(_candidate_features(candidate, i, last_seen, frequency))
                y.append(1 if candidate == optimal_victim else 0)
            frames.remove(optimal_victim)
            last_seen.pop(optimal_victim, None)

        frames.add(page)
        last_seen[page] = i

    return np.asarray(X, dtype=float), np.asarray(y, dtype=int)


def train_learned_model(training_trace: Sequence[int], frame_count: int,
                        max_depth: int = 4, random_state: int = 42) -> LearnedModel:
    X, y = build_training_data(training_trace, frame_count)
    if len(X) == 0 or len(set(y.tolist())) < 2:
        raise ValueError("Training trace did not produce enough replacement examples")

    clf = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=random_state,
    )
    clf.fit(X, y)
    return LearnedModel(clf)


def run_learned(trace: Sequence[int], frame_count: int, model: LearnedModel) -> PolicyRun:
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")

    frames: set[int] = set()
    last_seen: dict[int, int] = {}
    frequency: Counter[int] = Counter()
    events: list[AccessEvent] = []

    for i, page in enumerate(trace):
        frequency[page] += 1

        if page in frames:
            last_seen[page] = i
            events.append(AccessEvent(i, page, True, None))
            continue

        evicted = None
        if len(frames) >= frame_count:
            candidates = sorted(frames)
            features = [_candidate_features(p, i, last_seen, frequency) for p in candidates]
            scores = model.score_candidates(features)
            # Deterministic tie-break: candidate order is sorted.
            evicted = candidates[int(np.argmax(scores))]
            frames.remove(evicted)
            last_seen.pop(evicted, None)

        frames.add(page)
        last_seen[page] = i
        events.append(AccessEvent(i, page, False, evicted))

    return PolicyRun("Learned", frame_count, events)
