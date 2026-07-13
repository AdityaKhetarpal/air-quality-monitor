import sys
import time
import datetime

import requests
import pandas as pd

import config


def fetch_city(city: dict) -> dict | None:
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "hourly": "pm2_5",
    }

    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            # actual api call
            response = requests.get(
                config.AIR_QUALITY_API_URL,
                params=params,
                timeout=config.REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()

            # finding the actual reading out
            hourly = payload.get("hourly", {})
            pm25_values = hourly.get("pm2_5", [])
            timestamps = hourly.get("time", [])

            if not pm25_values or not timestamps:
                print(f"WARNING: {city['name']} returned no PM2.5 data", file=sys.stderr)
                return None

            # walk backward to find the most recent NON-NULL reading —
            # Open-Meteo's array includes future forecast hours that are
            # still None because the model hasn't computed them yet
            latest_pm25 = None
            latest_time = None
            for value, time_str in zip(reversed(pm25_values), reversed(timestamps)):
                if value is not None:
                    latest_pm25 = value
                    latest_time = time_str
                    break

            if latest_pm25 is None:
                print(f"WARNING: {city['name']} has no non-null PM2.5 readings", file=sys.stderr)
                return None

            return {
                "city": city["name"],
                "reading_time": latest_time,
                "pm2_5": latest_pm25,
                "fetched_at": datetime.datetime.utcnow().isoformat(),
            }

        except requests.exceptions.Timeout:
            print(f"Attempt {attempt}/{config.MAX_RETRIES}: {city['name']} timed out", file=sys.stderr)
        except requests.exceptions.ConnectionError:
            print(f"Attempt {attempt}/{config.MAX_RETRIES}: {city['name']} connection failed", file=sys.stderr)
        except requests.exceptions.HTTPError as exc:
            print(f"Attempt {attempt}/{config.MAX_RETRIES}: {city['name']} HTTP error — {exc}", file=sys.stderr)
        except (KeyError, ValueError) as exc:
            print(f"{city['name']} returned unexpected response shape — {exc}", file=sys.stderr)
            return None

        time.sleep(2)

    print(f"FAILED: {city['name']} — exhausted all {config.MAX_RETRIES} retries", file=sys.stderr)
    return None


def fetch_cities() -> tuple[list[dict], list[str]]:
    successes = []
    failures = []

    for city in config.CITIES:  # loop through 5 cities one at a time
        result = fetch_city(city)

        if result is not None:
            successes.append(result)
        else:
            print(f"ERROR: Could not fetch data for {city['name']} — skipping", file=sys.stderr)
            failures.append(city["name"])

    return successes, failures


def main():
    config.DATA_DIR.mkdir(exist_ok=True)  # path to the data folder in config.py file
    successes, failures = fetch_cities()

    if successes:
        df = pd.DataFrame(successes)
        df.to_csv(config.LIVE_READINGS_CSV, index=False)
        print(f"Wrote {len(df)} readings to {config.LIVE_READINGS_CSV}")
    else:
        print("ERROR: No cities returned data", file=sys.stderr)

    print(f"Summary: {len(successes)} succeeded, {len(failures)} failed"
          + (f" ({', '.join(failures)})" if failures else ""))


if __name__ == "__main__":
    main()