from src.learned import build_training_data, train_learned_model, run_learned
from src.workload import WorkloadConfig, generate_trace


def test_training_data_and_run():
    train = generate_trace(WorkloadConfig(total_accesses=2000, seed=7))
    test = generate_trace(WorkloadConfig(total_accesses=2000, seed=42))
    X, y = build_training_data(train, 5)
    assert len(X) == len(y)
    assert X.shape[1] == 2
    assert set(y.tolist()) == {0, 1}

    model = train_learned_model(train, 5)
    run = run_learned(test, 5, model)
    assert len(run.events) == len(test)
