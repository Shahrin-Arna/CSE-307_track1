from src.workload import WorkloadConfig, generate_trace


def test_deterministic_trace():
    cfg = WorkloadConfig(total_accesses=1000, seed=42)
    assert generate_trace(cfg) == generate_trace(cfg)


def test_trace_length_and_page_range():
    cfg = WorkloadConfig(total_accesses=1000, num_pages=50, seed=42)
    trace = generate_trace(cfg)
    assert len(trace) == 1000
    assert min(trace) >= 0
    assert max(trace) < 50
