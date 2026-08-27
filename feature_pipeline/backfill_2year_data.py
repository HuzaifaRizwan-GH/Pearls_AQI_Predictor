
import os, glob, pandas as pd, hopsworks

matches = glob.glob("**/historical_aqi_weather_2years.csv", recursive=True)
if not matches:
    matches = glob.glob("*2years*.csv", recursive=True)

csv_path = matches[0]
print("Found dataset at:", csv_path)

df = pd.read_csv(csv_path)
df["time"] = pd.to_datetime(df["time"])

df_fg = df.dropna(subset=["aqi_lag_72h", "aqi_rolling_72h"]).copy()
if "aqi_72h" in df_fg.columns:
    df_fg = df_fg.drop(columns=["aqi_72h"])

numeric_cols = [c for c in df_fg.columns if c != "time"]
for c in numeric_cols:
    df_fg[c] = pd.to_numeric(df_fg[c], errors="coerce")

df_fg = df_fg.dropna().reset_index(drop=True)
print(f"Clean rows ready for upload: {len(df_fg)} | columns: {len(df_fg.columns)}")

print("\nConnecting to Hopsworks...")
project = hopsworks.login(
    project="huzzproj10p",
    host="eu-west.cloud.hopsworks.ai",
    api_key_value="nCmu6z9w6K90pWsf.FwfjvKKa4zp2gzqdbALSUZNxbsaqa9Knu9MeHvHnysIiJadKHzvVUaPKGBaDrCBC"
)
fs = project.get_feature_store()

# Explicitly specifying time_travel_format="HUDI" for native Hopsworks ingestion
fg = fs.get_or_create_feature_group(
    name="aqi_historical_features",
    version=2,
    description="2-Year Karachi hourly weather & AQI features with lag columns",
    primary_key=["time"],
    event_time="time",
    online_enabled=False,
    time_travel_format="HUDI"
)

print("\nUploading 2-year feature dataset to Hopsworks Cloud...")
fg.insert(df_fg, write_options={"wait_for_job": True})
print("\n==================================================")
print(" SUCCESS: 2-Year Feature Dataset Uploaded Successfully!")
print("==================================================")

