import pandas as pd

MAX_GAP_HOURS = 3

# Numbers that change gradually: draw a straight line across the gap
SMOOTH = [
    "temperature", "humidity", "wind_speed", "uv_index",
    "us_aqi", "pm2_5", "pm10", "nitrogen_dioxide", "ozone",
    "sulphur_dioxide", "carbon_monoxide",
]

# Numbers where a straight line makes no sense: repeat the last value
REPEAT = ["wind_direction", "precipitation", "precipitation_probability"]


def impute(table):
    """Fill short gaps and count how many values were filled in each row."""
    table = table.sort_values("time").reset_index(drop=True)
    before = table.isna()

    for col in SMOOTH:
        table[col] = table[col].interpolate(
            method="linear", limit=MAX_GAP_HOURS, limit_area="inside"
        )
    for col in REPEAT:
        table[col] = table[col].ffill(limit=MAX_GAP_HOURS)

    after = table.isna()
    table["n_imputed"] = (before & ~after).sum(axis=1)
    return table


# This part only runs when we run this file directly, as a quick test
if __name__ == "__main__":
    from fuse import fuse_sources

    pd.set_option("display.width", 200)
    fused = fuse_sources()

    # Pretend the API was down for 2 hours, by deleting 2 temperature values
    test = fused.copy()
    test.loc[10:11, "temperature"] = float("nan")
    print("BEFORE (2 hours missing):")
    print(test.loc[8:13, ["time", "temperature"]])

    fixed = impute(test)
    print("\nAFTER:")
    print(fixed.loc[8:13, ["time", "temperature", "n_imputed"]])
    print("\nTotal values filled:", fixed["n_imputed"].sum())