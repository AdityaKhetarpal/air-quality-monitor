import numpy as np
import pandas as pd
import config

def load_dirty_data() -> pd.DataFrame:
    return pd.read_csv(config.DIRTY_READINGS_CSV) #read the messy CSV into DataFrame

def clean_city_names(df: pd.DataFrame) -> pd.DataFrame:
    df["city"] = df["city"].str.strip().str.title()
    return df

def parse_mixed_dates(df: pd.DataFrame) -> pd.DataFrame:
    parsed = pd.to_datetime(df["reading_time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    still_missing = parsed.isna()
    parsed[still_missing] = pd.to_datetime(
        df.loc[still_missing, "reading_time"], format="%d/%m/%Y %H:%M", errors="coerce"
    )
    df["reading_time"] = parsed
    return df

def standardize(df:pd.DataFrame) -> pd.DataFrame:
    df["pm2_5"] = pd.to_numeric(df["pm2_5"], errors="coerce")
    df.loc[df["pm2_5"] < 0, "pm2_5"] = np.nan
    df["is_missing"] = df["pm2_5"].isna()
    df["is_outlier"] = df["pm2_5"] > config.PM_25_OUTLIER_THRESHOLD
    return df

def duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset="reading_id", keep="first")
    removed = before - len(df)
    print(f"Removed {removed} duplicate row based on reading_id")
    return df

def main():
    df = load_dirty_data()
    df = clean_city_names(df)
    df = parse_mixed_dates(df)
    df = standardize(df)
    df = duplicates(df)

    df.to_csv(config.CLEAN_READINGS_CSV, index= False)

    missing_count = df["is_missing"].sum()
    outlier_count = df["is_outlier"].sum()
    print(f"Wrote {len(df)} cleaned rows to {config.CLEAN_READINGS_CSV}")
    print(f" {missing_count} row flagged missing")
    print(f" {outlier_count} row flagged outlier")

if __name__ == "__main__":
    main()