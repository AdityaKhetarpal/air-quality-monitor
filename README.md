# Urban Air Quality Risk Monitor

A production-style data pipeline that pulls live PM2.5 air-quality readings for five Indian cities, validates and models them in SQL, and monitors for WHO guideline breaches in real time.

## What this project does

- Pulls live PM2.5 readings from a public air-quality API (Open-Meteo), with retry logic and graceful handling of partial failures (fail-soft: one city failing doesn't block the others).
- Generates and cleans a deliberately messy dataset to simulate real-world data problems — missing values, impossible readings, inconsistent formatting, duplicates — see `extract_dirty.py` and `clean_dirty.py`.
- Loads both data sources into a shared SQLite database, tagged by origin.
- Runs four SQL analyses: current breaches, week-over-week trend, city ranking (`RANK()`/`DENSE_RANK()`), and a data-quality report.
- Polls the live API on an interval and logs breach alerts (`monitor.py`).

## Why this project

Built to practice the operational and engineering habits that don't show up in a typical exploratory-analysis project: resilient extraction from a live, sometimes-unreliable source; cross-validation against a second, deliberately dirty dataset; a persistent, queryable data model instead of a one-off notebook; and a continuous monitoring layer instead of only a retrospective analysis.

## Architecture

```
Open-Meteo API                extract_dirty.py (fake messy data)
      |                                |
extract_live.py                 clean_dirty.py
      |                                |
readings_live.csv     readings_dirty_cleaned.csv
      |________________________________|
                    |
                    v
            load_readings.py
                    |
                    v
              readings.db
                    |
                    v
            sql/queries.sql
                    |
                    v
            analysis results

monitor.py polls the live API directly and logs breaches,
independent of the batch pipeline above.
```

## Project structure

| File | Purpose |
|---|---|
| `config.py` | Central settings — thresholds, paths, cities, API config |
| `extract_live.py` | Pulls live PM2.5 data with retries and failure handling |
| `extract_dirty.py` | Generates a reproducible, deliberately messy dataset |
| `clean_dirty.py` | Cleans the messy dataset, flags missing/outlier readings |
| `load_readings.py` | Loads both sources into a shared SQLite database |
| `monitor.py` | Polls the live API and logs breach alerts |
| `sql/schema.sql` | Database schema |
| `sql/queries.sql` | Breach, trend, ranking, and data-quality queries |
| `docs/NOTES.md` | Assumptions, limitations, and stakeholder summary |

## Setup

```bash
pip install -r requirements.txt
```

## Running the pipeline

Run these in order from the project root:

```bash
python extract_live.py
python extract_dirty.py
python clean_dirty.py
python load_readings.py
python debug.py            # runs and prints every query in sql/queries.sql
python monitor.py --once   # single poll cycle; omit --once to run continuously
```

## Key findings

See [`docs/NOTES.md`](docs/NOTES.md) for the full write-up, including the stakeholder summary, scope decisions, known limitations, and real bugs encountered and fixed during development.

## Tech stack

Python, pandas, requests, SQLite, SQL (window functions, aggregates), git.