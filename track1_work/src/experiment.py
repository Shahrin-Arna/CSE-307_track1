from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .fifo import run_fifo
from .learned import train_learned_model, run_learned
from .lru import run_lru
from .optimal import run_optimal
from .workload import WorkloadConfig, generate_trace


def run_experiment(output_dir: Path, accesses: int = 10_000,
                   frame_sizes: tuple[int, ...] = (3, 5, 10),
                   evaluation_seed: int = 42,
                   training_seed: int = 7) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)

    eval_trace = generate_trace(WorkloadConfig(total_accesses=accesses, seed=evaluation_seed))
    # Separate trace prevents training/evaluation leakage.
    train_trace = generate_trace(WorkloadConfig(total_accesses=accesses, seed=training_seed))

    rows: list[dict] = []

    for frames in frame_sizes:
        learned_model = train_learned_model(train_trace, frames)
        runs = [
            run_fifo(eval_trace, frames),
            run_lru(eval_trace, frames),
            run_optimal(eval_trace, frames),
            run_learned(eval_trace, frames, learned_model),
        ]
        for run in runs:
            rows.extend(run.before_after_metrics())

    df = pd.DataFrame(rows)
    df.to_csv(output_dir / "raw_results.csv", index=False)

    _plot_faults(df, output_dir / "page_faults.png")
    _plot_hit_ratio(df, output_dir / "hit_ratio.png")
    _write_summary(df, output_dir / "summary.txt")

    return df


def _ordered_pivot(df: pd.DataFrame, value: str) -> pd.DataFrame:
    policy_order = ["FIFO", "LRU", "Optimal", "Learned"]
    work = df.copy()
    work["policy"] = pd.Categorical(work["policy"], categories=policy_order, ordered=True)
    pivot = work.pivot_table(
        index=["policy", "frames"], columns="phase", values=value, observed=False
    ).sort_index()
    return pivot[["before_shift", "after_shift"]]


def _plot_faults(df: pd.DataFrame, path: Path) -> None:
    pivot = _ordered_pivot(df, "faults")
    ax = pivot.plot(kind="bar", figsize=(10, 6))
    ax.set_title("Page Faults Before vs After Workload Shift")
    ax.set_xlabel("Policy / Frames")
    ax.set_ylabel("Page Faults (per 5,000 accesses)")
    ax.legend(["Before shift", "After shift"], title="Phase")
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def _plot_hit_ratio(df: pd.DataFrame, path: Path) -> None:
    pivot = _ordered_pivot(df, "hit_ratio")
    ax = pivot.plot(kind="bar", figsize=(10, 6))
    ax.set_title("Hit Ratio Before vs After Workload Shift")
    ax.set_xlabel("Policy / Frames")
    ax.set_ylabel("Hit Ratio")
    ax.set_ylim(0, 1)
    ax.legend(["Before shift", "After shift"], title="Phase")
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def _write_summary(df: pd.DataFrame, path: Path) -> None:
    lines = []
    for frames in sorted(df["frames"].unique()):
        lines.append(f"Frames = {frames}")
        subset = df[df["frames"] == frames]
        for policy in ["FIFO", "LRU", "Optimal", "Learned"]:
            p = subset[subset["policy"] == policy].set_index("phase")
            before = p.loc["before_shift"]
            after = p.loc["after_shift"]
            delta = after["hit_ratio"] - before["hit_ratio"]
            lines.append(
                f"  {policy:8s} before={before['hit_ratio']:.4f} "
                f"after={after['hit_ratio']:.4f} delta={delta:+.4f}"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Track 1 page-replacement experiment")
    parser.add_argument("--output", default="results", help="Output directory")
    parser.add_argument("--accesses", type=int, default=10_000)
    args = parser.parse_args()

    df = run_experiment(Path(args.output), accesses=args.accesses)
    pd.set_option("display.max_rows", None)
    print(df.to_string(index=False, formatters={"hit_ratio": "{:.4f}".format, "fault_ratio": "{:.4f}".format}))


if __name__ == "__main__":
    main()
