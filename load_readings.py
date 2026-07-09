import sqlite3

import pandas as pd

import config


def prepare_live_data() -> pd.DataFrame:
    df = pd.read_csv(config.LIVE_READINGS_CSV)
    df["pm2_5"] = pd.to_numeric(df["pm2_5"], errors="coerce")
    df.loc[df["pm2_5"] < 0, "pm2_5"] = None

    df["is_missing"] = df["pm2_5"].isna().astype(int)
    df["is_outlier"] = (df["pm2_5"] > config.PM_25_OUTLIER_THRESHOLD).astype(int)
    df["source"] = "live"
    df["source_reading_id"] = range(1, len(df) + 1)

    return df[["source_reading_id", "city", "reading_time", "pm2_5", "is_missing", "is_outlier", "source"]]


def prepare_dirty_data() -> pd.DataFrame:
    df = pd.read_csv(config.CLEAN_READINGS_CSV)
    df["is_missing"] = df["is_missing"].astype(int)
    df["is_outlier"] = df["is_outlier"].astype(int)
    df["source"] = "dirty"

    return df[["reading_id", "city", "reading_time", "pm2_5", "is_missing", "is_outlier", "source"]].rename(
        columns={"reading_id": "source_reading_id"}
    )

def main():
    conn = sqlite3.connect(config.DB_PATH)
    conn.executescript(config.BASE_DIR.joinpath("sql", "schema.sql").read_text())

    live_df = prepare_live_data()
    dirty_df = prepare_dirty_data()

    live_df.to_sql("readings", conn,if_exists="append",index=False)
    dirty_df.to_sql("readings", conn,if_exists="append",index=False)

    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
    print(f"Loaded {len(live_df)} live rows and {len(dirty_df)} dirty rows")
    print(f"Total rows in readings table: {total}")

    conn.close()


if __name__ == "__main__":
    main()