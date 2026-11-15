import pandas as pd

# The columns we compute rolling averages and changes for
KEY_COLUMNS = ["temperature", "humidity", "wind_speed", "us_aqi", "pm2_5"]


def add_features(table):
    """Add time-based and derived features to the table."""
    table = table.sort_values("time").reset_index(drop=True)

    # 1) Time-based features
    table["hour"] = table["time"].dt.hour
    table["day"] = table["time"].dt.day
    table["month"] = table["time"].dt.month
    table["day_of_week"] = table["time"].dt.day_of_week  # Monday = 0

    # 2) Rate of change: how much a value changed compared to earlier
    for col in KEY_COLUMNS:
        table[f"{col}_change_1h"] = table[col].diff(1)
        table[f"{col}_change_3h"] = table[col].diff(3)

    # 3) Rolling averages: the average of the last few hours
    for col in KEY_COLUMNS:
        table[f"{col}_avg_3h"] = table[col].rolling(3, min_periods=1).mean()
        table[f"{col}_avg_24h"] = table[col].rolling(24, min_periods=1).mean()

    return table


# This part only runs when we run this file directly, as a quick test
if __name__ == "__main__":
    from fuse import fuse_sources
    from impute import impute

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    table = add_features(impute(fuse_sources()))
    print("Size (rows, columns):", table.shape)

    show = ["time", "hour", "day", "month", "temperature",
            "temperature_change_1h", "temperature_avg_3h", "temperature_avg_24h"]
    print(table[show].tail(5))