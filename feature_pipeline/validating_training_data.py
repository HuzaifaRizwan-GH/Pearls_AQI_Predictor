import pandas as pd


INPUT_FILE = "data/historical_aqi_features.csv"

# Load dataset
df = pd.read_csv(INPUT_FILE)

print("========================================")
print("TRAINING DATA VALIDATION")
print("========================================")

# 1. Number of rows and columns
print(f"\nRows: {len(df)}")
print(f"Columns: {len(df.columns)}")

# 2. Check duplicate timestamps
duplicate_times = df["time"].duplicated().sum()
print(f"\nDuplicate timestamps: {duplicate_times}")

# 3. Check missing values
missing_values = df.isnull().sum()

print("\nMissing values:")
print(missing_values[missing_values > 0])

# 4. Check AQI
print("\nAQI statistics:")
print(f"Minimum AQI: {df['aqi'].min()}")
print(f"Maximum AQI: {df['aqi'].max()}")
print(f"Average AQI: {df['aqi'].mean():.2f}")

# 5. Check required columns
required_columns = [
    "time",
    "pm2_5",
    "pm10",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "temperature_2m",
    "relative_humidity_2m",
    "surface_pressure",
    "wind_speed_10m",
    "precipitation",
    "hour",
    "day",
    "month",
    "day_of_week",
    "pm2_5_change",
    "pm10_change",
    "pm2_5_change_rate",
    "pm10_change_rate",
    "aqi",
    "aqi_change",
    "aqi_change_rate"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

print("\nMissing required columns:")
print(missing_columns)

# 6. Final result
if (
    len(df) == 2160
    and duplicate_times == 0
    and len(missing_columns) == 0
):
    print("\n BASIC VALIDATION PASSED")
else:
    print("\n VALIDATION NEEDS ATTENTION")

print("\nTraining dataset is ready for the next pipeline step.")