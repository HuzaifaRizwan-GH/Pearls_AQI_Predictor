import pandas as pd


INPUT_FILE = "data/historical_raw_data.csv"
OUTPUT_FILE = "data/historical_features.csv"


# Load historical raw data
df = pd.read_csv(INPUT_FILE)

# Convert time to datetime
df["time"] = pd.to_datetime(df["time"])

# Sort chronologically
df = df.sort_values("time").reset_index(drop=True)


# Time-based features
df["hour"] = df["time"].dt.hour
df["day"] = df["time"].dt.day
df["month"] = df["time"].dt.month
df["day_of_week"] = df["time"].dt.dayofweek


# Pollutant change features
df["pm2_5_change"] = df["pm2_5"].diff()
df["pm10_change"] = df["pm10"].diff()

# Pollutant change rates
df["pm2_5_change_rate"] = df["pm2_5"].pct_change() * 100
df["pm10_change_rate"] = df["pm10"].pct_change() * 100


# Save
df.to_csv(OUTPUT_FILE, index=False)

print("Historical feature engineering successful!")
print(f"Rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"Historical features saved to: {OUTPUT_FILE}")