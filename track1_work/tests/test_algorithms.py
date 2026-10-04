from src.fifo import run_fifo
from src.lru import run_lru
from src.optimal import run_optimal


def faults(run):
    return sum(not e.hit for e in run.events)


def test_known_reference_trace_three_frames():
    trace = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    assert faults(run_fifo(trace, 3)) == 10
    assert faults(run_lru(trace, 3)) == 9
    assert faults(run_optimal(trace, 3)) == 7


def test_optimal_not_worse_than_fifo_or_lru():
    trace = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    opt = faults(run_optimal(trace, 3))
    assert opt <= faults(run_fifo(trace, 3))
    assert opt <= faults(run_lru(trace, 3))
