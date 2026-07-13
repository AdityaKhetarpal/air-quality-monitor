import sqlite3

import pandas as pd

import config


def main():
    config.POWERBI_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)

    breaches = pd.read_sql_query(
        """
        SELECT city, reading_time, pm2_5, is_outlier, source
        FROM readings
        WHERE pm2_5 > ?
        ORDER BY pm2_5 DESC
        """,
        conn,
        params=(config.PM25_BREACH_THRESHOLD,),
    )
    breaches.to_csv(config.POWERBI_DIR / "breaches.csv", index=False)

    trend = pd.read_sql_query(
        f"""
        SELECT
            city,
            ROUND(AVG(CASE WHEN reading_time >= DATETIME('{config.REFERENCE_DATE}', '-7 days') THEN pm2_5 END), 1) AS avg_this_week,
            ROUND(AVG(CASE WHEN reading_time < DATETIME('{config.REFERENCE_DATE}', '-7 days')
                           AND reading_time >= DATETIME('{config.REFERENCE_DATE}', '-14 days') THEN pm2_5 END), 1) AS avg_last_week
        FROM readings
        WHERE is_missing = 0 AND is_outlier = 0
        GROUP BY city
        """,
        conn,
    )
    
    def label_trend(row):
        if pd.isna(row["avg_this_week"]) or pd.isna(row["avg_last_week"]):
            return "Insufficient data"
        elif row["avg_this_week"] > row["avg_last_week"]:
            return "Worse"
        else:
            return "Better or same"

    trend["trend"] = trend.apply(label_trend, axis=1)

    trend.to_csv(config.POWERBI_DIR / "trend.csv", index=False)

    ranking = pd.read_sql_query(
        """
        SELECT
            city,
            ROUND(AVG(pm2_5), 1) AS avg_pm2_5,
            RANK() OVER (ORDER BY AVG(pm2_5) DESC) AS rank_by_avg
        FROM readings
        WHERE is_missing = 0 AND is_outlier = 0
        GROUP BY city
        ORDER BY avg_pm2_5 DESC
        """,
        conn,
    )
    ranking.to_csv(config.POWERBI_DIR / "ranking.csv", index=False)

    quality = pd.read_sql_query(
        """
        SELECT
            city,
            source,
            COUNT(*) AS total_readings,
            SUM(is_missing) AS missing_count,
            ROUND(100.0 * SUM(is_missing) / COUNT(*), 1) AS pct_missing,
            SUM(is_outlier) AS outlier_count,
            ROUND(100.0 * SUM(is_outlier) / COUNT(*), 1) AS pct_outlier
        FROM readings
        GROUP BY city, source
        ORDER BY city, source
        """,
        conn,
    )
    quality.to_csv(config.POWERBI_DIR / "data_quality.csv", index=False)

    conn.close()
    print(f"Exported 4 CSVs to {config.POWERBI_DIR}:")
    print(f"  breaches.csv     ({len(breaches)} rows)")
    print(f"  trend.csv        ({len(trend)} rows)")
    print(f"  ranking.csv      ({len(ranking)} rows)")
    print(f"  data_quality.csv ({len(quality)} rows)")


if __name__ == "__main__":
    main()