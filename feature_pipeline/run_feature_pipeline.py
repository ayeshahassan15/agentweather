from fuse import fuse_sources, get_raw_table
from impute import impute
from features import add_features
from hopsworks_connect import connect


def run():
    # 1) Fetch the raw data from the sources
    raw = get_raw_table()
    print("Raw table:", raw.shape)

    # 2) Combine, fill short gaps, add features
    table = add_features(impute(fuse_sources(raw)))
    print("Feature table:", table.shape)

    # 3) Upload both to Hopsworks
    project, fs = connect()

    raw_group = fs.get_or_create_feature_group(
        name="raw_observations",
        version=1,
        description="Raw hourly data from Open-Meteo and OpenWeather for Karachi",
        primary_key=["time"],
        event_time="time",
        time_travel_format="DELTA",
        stream=True,
    )
    raw_group.insert(raw, wait=True)
    print("Uploaded", len(raw), "rows to raw_observations")

    feature_group = fs.get_or_create_feature_group(
        name="weather_features",
        version=2,
        description="Hourly fused weather and air quality features for Karachi",
        primary_key=["time"],
        event_time="time",
        time_travel_format="DELTA",
        stream=True,
    )
    feature_group.insert(table, wait=True)
    print("Uploaded", len(table), "rows to weather_features")


if __name__ == "__main__":
    run()