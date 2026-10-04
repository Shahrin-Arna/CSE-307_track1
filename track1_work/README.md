# Learned Page Replacement

This project compares four page-replacement policies under a changing memory-access workload:

- FIFO
- LRU
- Optimal (Belady's)
- Learned replacement using a Decision Tree

The workload has two phases. The first half uses a locality-heavy access pattern, while the second half changes to a random/bursty pattern. Each policy is tested on the same trace.

The learned policy uses two features for pages currently in memory:

- recency
- access frequency

A separate training trace is used for the classifier. Optimal replacement decisions are used to label good eviction candidates during training.

## Setup

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Run

Run the experiment from the project folder:

```bash
python -m src.experiment
```

Run the tests with:

```bash
python -m pytest -q
```

## Results

The experiment records page faults and hit ratios before and after the workload shift for 3, 5, and 10 frames.

Generated results are stored in `results/`:

- `raw_results.csv`
- `page_faults.png`
- `hit_ratio.png`

The same workload was also run in Ubuntu on VMware using different RAM and vCPU configurations. Those system-level measurements are stored in `vm_results/vm_measurements.csv`.

## Project Structure

```text
track1_work/
├── README.md
├── requirements.txt
├── src/
├── tests/
├── results/
└── vm_results/
```

## AI Assistance

AI tools were used to assist. The experiments were run in different vm config and the results were collected by me.
