import pandas as pd


INPUT_FILE = "data/historical_features.csv"
OUTPUT_FILE = "data/historical_aqi_features.csv"


def calculate_pm25_aqi(pm25):
    """
    Calculate US EPA AQI from PM2.5 concentration.
    Concentration unit: µg/m³
    """

    breakpoints = [
        (0.0, 9.0, 0, 50),
        (9.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 125.4, 151, 200),
        (125.5, 225.4, 201, 300),
        (225.5, 325.4, 301, 500),
    ]

    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= pm25 <= c_high:
            aqi = (
                ((i_high - i_low) / (c_high - c_low))
                * (pm25 - c_low)
                + i_low
            )

            return round(aqi)

    return None


# Load historical features
df = pd.read_csv(INPUT_FILE)

# Calculate AQI
df["aqi"] = df["pm2_5"].apply(calculate_pm25_aqi)

# Calculate AQI change
df["aqi_change"] = df["aqi"].diff()

# Calculate AQI change rate
df["aqi_change_rate"] = df["aqi"].pct_change() * 100

# Save final historical dataset
df.to_csv(OUTPUT_FILE, index=False)

print("Historical AQI calculation successful!")
print(f"Rows: {len(df)}")
print(f"AQI minimum: {df['aqi'].min()}")
print(f"AQI maximum: {df['aqi'].max()}")
print(f"Columns: {list(df.columns)}")
print(f"Historical AQI dataset saved to: {OUTPUT_FILE}")