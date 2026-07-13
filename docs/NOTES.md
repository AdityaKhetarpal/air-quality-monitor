# Urban Air Quality Risk Monitor — Notes

## Stakeholder summary

As of this pull, four of the five monitored cities — Delhi, Mumbai, Kolkata, and
Chennai — are breaching the WHO's safe 24-hour PM2.5 guideline of 15 µg/m³, with
Delhi's reading (136.4 µg/m³) nearly nine times the safe level. Chennai and Mumbai
are also trending worse week-over-week, meaning their air quality has been getting
worse, not just staying bad. This data comes from a live public air-quality feed,
and our pipeline includes automatic checks to catch and flag unreliable sensor
readings before they affect these numbers — none of the current breaches were
flagged as unreliable. We'd recommend prioritizing Delhi and Chennai for immediate
attention given the severity and trend, respectively.

## Scope decisions

- Used raw PM2.5 concentration rather than a composite AQI (which blends multiple
  pollutants via piecewise conversion tables), to keep the project buildable while
  staying scientifically grounded.
- Breach threshold set at 15 µg/m³, the WHO 2021 24-hour PM2.5 guideline — not the
  more lenient US EPA "Unhealthy for Sensitive Groups" threshold (35.5 µg/m³) —
  chosen because a monitoring/alerting use case should favor catching problems
  early over waiting for a crisis-level reading.
- monitor.py logs a breach alert on *every* poll cycle for as long as a city stays
  over threshold, rather than deduplicating (only alerting on new breaches). This
  was a deliberate choice for a complete audit trail; in a real production
  deployment with a human on-call, deduplication (as in the original assignment's
  wallet-concentration monitor) would likely be the better default to avoid alert
  fatigue.

## Data sources

- **Live**: Open-Meteo's free air-quality API, pulled per-city for Delhi, Mumbai,
  Bengaluru, Kolkata, and Chennai. No API key required.
- **Dirty/test**: a deliberately fabricated dataset (extract_dirty.py) simulating
  common real-world data problems — missing values (both blank and literal "N/A"),
  physically impossible readings (negative PM2.5), extreme outliers, inconsistent
  city name casing/whitespace, mixed date formats, and duplicate rows — used to
  validate the cleaning pipeline, not as a second real-world data source. The two
  are kept distinguishable via a `source` column in the shared database.

## Known limitations

- **Live sample size is small.** Each pull captures one reading per city, so the
  data-quality percentages (Query 4) aren't statistically meaningful yet for the
  live source specifically — they'll become genuinely useful once monitor.py has
  accumulated readings over many polls.
- **Query 2's trend comparison currently uses the real system clock (`'now'`)**,
  compared against fixed test data generated for a specific week in July 2026.
  This only produces meaningful results when the real date happens to be within
  ~14 days of that window. `config.REFERENCE_DATE` exists as a placeholder for a
  proper fix — swapping the query to compare against a configurable anchor date
  instead of `'now'` — but this hasn't been wired in yet.
- **A real bug we hit and fixed**: extract_live.py originally grabbed the *last*
  element of the API's PM2.5 array (`pm25_values[-1]`) to get the most recent
  reading. This silently failed, because Open-Meteo's hourly array includes future
  forecast hours that come back as `None` until the model computes them — so the
  "latest" index was actually a not-yet-computed future value, not the most recent
  real reading. Every city "succeeded" (the array wasn't empty) but every value was
  blank, and this only surfaced when Query 4's data-quality report showed 100%
  missing on all live data. Fixed by scanning backward through the array for the
  most recent non-null value instead of blindly indexing the last position.
- **Config naming drift**: several config.py constant names drifted out of sync
  with what depending scripts expected (e.g. `PM_25_OUTLIER_THRESHOLD` vs.
  `PM25_OUTLIER_THRESHOLD`) after manual edits. Nothing currently catches this
  automatically before runtime — a linter would catch this class of error earlier.

## Production improvements

- Deduplicate monitor.py alerts (only log new breaches, not every poll) if this
  moved from an audit-trail use case to an on-call alerting use case.
- Fix Query 2 to compare against `config.REFERENCE_DATE` in test/demo mode, while
  still using real `'now'` for live monitoring.
- Persist monitor.py's poll history to the database instead of only to a log file,
  so historical trend queries could run against live data too, not just the fixed
  test window.
- Add a linter (e.g. flake8 or ruff) to catch naming mismatches like the config
  drift automatically, before runtime.
- Push monitor.py alerts to Slack/email instead of only a local log file.