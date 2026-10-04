from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class WorkloadConfig:
    total_accesses: int = 10_000
    num_pages: int = 50
    locality_set_size: int = 3
    locality_probability: float = 0.90
    burst_min_len: int = 20
    burst_max_len: int = 80
    burst_set_size: int = 8
    seed: int = 42


def _validate(cfg: WorkloadConfig) -> None:
    if cfg.total_accesses < 2:
        raise ValueError("total_accesses must be at least 2")
    if cfg.num_pages < 2:
        raise ValueError("num_pages must be at least 2")
    if not 1 <= cfg.locality_set_size < cfg.num_pages:
        raise ValueError("locality_set_size must be between 1 and num_pages-1")
    if not 0.0 <= cfg.locality_probability <= 1.0:
        raise ValueError("locality_probability must be in [0, 1]")
    if not 1 <= cfg.burst_set_size <= cfg.num_pages:
        raise ValueError("burst_set_size must be between 1 and num_pages")


def generate_trace(cfg: WorkloadConfig = WorkloadConfig()) -> List[int]:
    """Generate a deterministic trace with a deliberate halfway workload shift.

    First half:
        Locality-heavy, mostly sequential accesses over a small hot set with
        occasional accesses elsewhere.

    Second half:
        Bursty/random accesses. Each burst selects a fresh working set and
        repeatedly samples from it before switching to another set.
    """
    _validate(cfg)
    rng = random.Random(cfg.seed)

    first_len = cfg.total_accesses // 2
    second_len = cfg.total_accesses - first_len

    hot_pages = list(range(cfg.locality_set_size))
    cold_pages = list(range(cfg.locality_set_size, cfg.num_pages))

    first_half: List[int] = []
    seq_index = 0
    for _ in range(first_len):
        if rng.random() < cfg.locality_probability:
            first_half.append(hot_pages[seq_index % len(hot_pages)])
            seq_index += 1
        else:
            first_half.append(rng.choice(cold_pages))

    second_half: List[int] = []
    all_pages = list(range(cfg.num_pages))
    while len(second_half) < second_len:
        burst_len = rng.randint(cfg.burst_min_len, cfg.burst_max_len)
        burst_pages = rng.sample(all_pages, k=min(cfg.burst_set_size, cfg.num_pages))
        for _ in range(min(burst_len, second_len - len(second_half))):
            # Mostly stay inside the current burst set, sometimes jump anywhere.
            if rng.random() < 0.85:
                second_half.append(rng.choice(burst_pages))
            else:
                second_half.append(rng.choice(all_pages))

    return first_half + second_half


def split_trace(trace: List[int]) -> tuple[List[int], List[int]]:
    midpoint = len(trace) // 2
    return trace[:midpoint], trace[midpoint:]
