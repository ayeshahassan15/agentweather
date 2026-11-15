import pandas as pd
import config
from fetch_data import (
    fetch_openmeteo_weather,
    fetch_openmeteo_air_quality,
    fetch_openweather_weather,
    fetch_openweather_pollution,
)


def fuse_sources():
    """Fetch all four sources and combine them into one table, one row per hour."""
    om_weather = fetch_openmeteo_weather()
    om_air = fetch_openmeteo_air_quality()
    ow_weather = fetch_openweather_weather()
    ow_pollution = fetch_openweather_pollution()

    # Join the tables side by side, matching rows that have the same time
    table = om_weather.merge(om_air, on="time", how="outer")
    table = table.merge(ow_weather, on="time", how="left")
    table = table.merge(ow_pollution, on="time", how="left")

    # Open-Meteo also lists hours that have not happened yet (predictions).
    # Keep only hours up to now.
    now = pd.Timestamp.now(tz=config.TIMEZONE).tz_localize(None).floor("h")
    table = table[table["time"] <= now].copy()

    # Rule 1: average (mean() ignores a missing value)
    table["temperature"] = table[["temperature_2m", "ow_temperature"]].mean(axis=1)
    table["humidity"] = table[["relative_humidity_2m", "ow_humidity"]].mean(axis=1)
    table["wind_speed"] = table[["wind_speed_10m", "ow_wind_speed"]].mean(axis=1)

    # Rule 2: priority (OpenWeather first, Open-Meteo if it is missing)
    table["wind_direction"] = table["ow_wind_direction"].fillna(
        table["wind_direction_10m"]
    )

    return table


# This part only runs when we run this file directly, as a quick test
if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    fused = fuse_sources()
    print("Size (rows, columns):", fused.shape)
    show = ["time", "temperature_2m", "ow_temperature", "temperature",
            "humidity", "wind_speed", "wind_direction"]
    print(fused[show].tail(4))