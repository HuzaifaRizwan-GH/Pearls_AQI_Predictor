import pandas as pd


# Input and output files
INPUT_FILE = "data/raw_data.csv"
OUTPUT_FILE = "data/features.csv"


# 1. Load raw data
df = pd.read_csv(INPUT_FILE)


# 2. Convert time column to datetime
df["time"] = pd.to_datetime(df["time"])


# 3. Create time-based features
df["hour"] = df["time"].dt.hour
df["day"] = df["time"].dt.day
df["month"] = df["time"].dt.month
df["day_of_week"] = df["time"].dt.dayofweek


# 4. Create pollutant change features
df["pm2_5_change"] = df["pm2_5"].diff()
df["pm10_change"] = df["pm10"].diff()


# 5. Create pollutant change rate
df["pm2_5_change_rate"] = (
    df["pm2_5"].pct_change() * 100
)


# 6. Save feature dataset
df.to_csv(OUTPUT_FILE, index=False)


print("Feature engineering successful!")
print(f"Rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"Features saved to: {OUTPUT_FILE}")