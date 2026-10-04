# Learned Page Replacement

This project compares four page-replacement policies:

- FIFO
- LRU
- Optimal (Belady's)
- Learned replacement using a Decision Tree

The workload changes halfway through the experiment. The first half follows a locality-heavy access pattern, while the second half changes to a random/bursty pattern.

All policies are tested using the same workload.

The learned policy uses:

- recency
- access frequency

A separate trace is used to train the classifier, and Optimal replacement is used to label the eviction choices during training.

## Setup

Install the required packages:

```bash
pip install -r requirements.txt
```

## Run

Run the experiment:

```bash
python -m src.experiment
```

Run the tests:

```bash
python -m pytest -q
```

## Results

The experiment records page faults and hit ratios before and after the workload shift for 3, 5, and 10 frames.

Results are saved in the `results/` folder:

- `raw_results.csv`
- `page_faults.png`
- `hit_ratio.png`

The same workload was also tested in Ubuntu using VMware with different RAM and vCPU configurations. The VM measurements are stored in:

```text
vm_results/vm_measurements.csv
```

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

AI tools were used for implementation assistance and debugging. The experiments were run and the results were collected using my own system and VM configurations.
