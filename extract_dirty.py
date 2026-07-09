import random #to pick random cities,values and format
import datetime #to make fake timestamps

import pandas as pd

import config

random.seed(config.RANDOM_SEED) #starts randomness generator at a fixed starting point (42, from config)

CITY_NAME_VARIANTS = {
    "Delhi": ["Delhi","delhi"," Delhi ","DELHI"],
    "Mumbai": ["Mumbai","mumbai", " Mumbai ", "MUMBAI"],
    "Bengaluru": ["Bengaluru", "bengaluru", " Bengaluru ", "BENGALURU"],
    "Kolkata": ["Kolkata","kolkata"," Kolkata ", "KOLKATA"],
    "Chennai": ["Chennai", "chennai", " Chennai ", "CHENNAI"]
}

def random_timestamp():
    base = datetime.datetime(2026, 7, 1) # a fixed starting date
    offset_hours = random.randint(0, 24 * 7)
    ts = base + datetime.timedelta(hours=offset_hours)
    if random.random() < 0.5: #random.random() gives random decimal between 0.0 and 1.0
        return ts.strftime("%Y-%m-%d %H:%M:%S") #2026-07-03 14:00:00
    else:
        return ts.strftime("%d/%m/%Y %H:%M") #03/07/2026 14:00
    
def random_pm25():
    roll =  random.random()
    if roll < 0.05:
        return None
    elif roll < 0.10:
        return "N/A" #different way of representing missing
    elif roll < 0.15:
        return -5.0
    elif roll < 0.20:
        return 5000.0
    else:
        return round(random.uniform(5,120), 1)
    
def generate_dirty_rows(n=40): #a default parameter: generate 40 rows unless told otherwise
    rows = []
    cities = list(CITY_NAME_VARIANTS.keys())
    for i in range(1, n+1): #loops 40 times
        city_key = random.choice(cities)
        city_name = random.choice(CITY_NAME_VARIANTS[city_key])
        rows.append({
            "reading_id": i,
            "city": city_name,
            "reading_time": random_timestamp(),
            "pm2_5": random_pm25(),
        })
    duplicates = random.sample(rows,k=4)
    rows.extend(duplicates)
    return rows
    
def main():
    config.DATA_DIR.mkdir(exist_ok=True)
    rows = generate_dirty_rows()
    df = pd.DataFrame(rows)
    df.to_csv(config.DIRTY_READINGS_CSV,index=False)
    print(f"Wrote {len(df)} (deliberately messy) rows to {config.DIRTY_READINGS_CSV}")

if __name__  == "__main__":
    main()