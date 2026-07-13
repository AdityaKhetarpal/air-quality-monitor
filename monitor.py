import sys
import time
import logging
import argparse

import config
from extract_live import fetch_city


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
    logging.StreamHandler(sys.stdout),
    logging.FileHandler(config.LOGS_DIR / "monitoring.log", encoding="utf-8"),
],
)
logger = logging.getLogger("monitor")


def poll_once():
    readings = []
    for city in config.CITIES:
        result = fetch_city(city)
        if result is not None:
            readings.append(result)
        else:
            logger.info(f"WARNING — could not fetch a reading for {city['name']} this poll")

    breaches = [r for r in readings if r["pm2_5"] > config.PM25_BREACH_THRESHOLD]

    if breaches:
        for b in breaches:
            logger.info(
                f"ALERT — {b['city']} PM2.5 = {b['pm2_5']} exceeds "
                f"{config.PM25_BREACH_THRESHOLD} µg/m³ threshold"
            )
    else:
        logger.info(f"OK — no city exceeded {config.PM25_BREACH_THRESHOLD} µg/m³ this poll")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="run a single poll cycle and exit")
    args = parser.parse_args()

    config.LOGS_DIR.mkdir(exist_ok=True)
    logger.info(
        f"Monitor started (threshold={config.PM25_BREACH_THRESHOLD} µg/m³, "
        f"interval={config.POLL_INTERVAL_SECONDS}s)"
    )

    while True:
        poll_once()

        if args.once:
            break
        time.sleep(config.POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main() 