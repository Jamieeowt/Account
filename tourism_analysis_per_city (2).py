"""
Philippine Tourism Data — Per-City Statistical Analysis (no matplotlib)
=======================================================================

Runs the analysis for EACH city (Destination) separately. For every city it
reports the same techniques, then prints cross-city comparison/ranking tables.

Per-city techniques:
  Mean / Median        | NumberOfVisitors, AvgSpendingPHP, AvgStayDays,
                       | SatisfactionRating
  Mode                 | Province, IslandGroup, Month, Season (city's own)
  Standard deviation   | NumberOfVisitors, AvgSpendingPHP, AvgStayDays
  Min / Max            | NumberOfVisitors, AvgSpendingPHP, AvgStayDays
  Correlation          | numeric vs numeric (if enough rows)
  Trend analysis       | Year / Season vs NumberOfVisitors & AvgSpendingPHP
  Frequency dist.      | Month, Season (counts per category)

Notes:
  * Median preferred over mean — data has noisy outliers (negatives, ratings > 5).
  * Min/Max flags invalid negative values.
  * Correlation needs >= 3 rows; skipped for tiny cities.
"""

import sys
from pathlib import Path

import pandas as pd

CSV_FILE = "cleaned_philippines_tourism_data.csv"
CITY_COL = "Destination"

NUMERIC_FULL = [
    "NumberOfVisitors",
    "AvgSpendingPHP",
    "AvgStayDays",
    "SatisfactionRating",
]
NUMERIC_CORE = ["NumberOfVisitors", "AvgSpendingPHP", "AvgStayDays"]
# Per-city categoricals (Destination is the split key, so excluded here).
CITY_CATEGORICAL = ["Month", "Season"]

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def banner(title, char="="):
    line = char * 70
    print(f"\n{line}\n{title}\n{line}")


def load_data(path):
    if not Path(path).exists():
        sys.exit(f"ERROR: could not find '{path}'. Run this from the data folder.")
    df = pd.read_csv(path)
    for col in NUMERIC_FULL:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _ordered_months(values):
    present = [m for m in MONTH_ORDER if m in set(values)]
    return present if present else sorted(set(values))


# --------------------------------------------------------------------------- #
# Per-city report
# --------------------------------------------------------------------------- #
def analyze_city(name, cdf):
    banner(f"CITY: {name}   ({len(cdf)} records)", char="#")

    num_full = [c for c in NUMERIC_FULL if c in cdf.columns]
    num_core = [c for c in NUMERIC_CORE if c in cdf.columns]

    # --- Mean / Median ---
    print("\n[Mean & Median]  (median preferred - noisy outliers)")
    stats = pd.DataFrame(
        {
            "Mean": cdf[num_full].mean(numeric_only=True),
            "Median": cdf[num_full].median(numeric_only=True),
        }
    )
    print(stats.round(2).to_string())

    # --- Standard deviation ---
    print("\n[Standard deviation]  (spread / variability)")
    sd = pd.DataFrame(
        {
            "Mean": cdf[num_core].mean(numeric_only=True),
            "StdDev": cdf[num_core].std(numeric_only=True),
        }
    )
    print(sd.round(2).to_string())

    # --- Min / Max + invalid negatives ---
    print("\n[Min / Max]  (peak vs. lowest; flags invalid negatives)")
    mm = pd.DataFrame(
        {
            "Min": cdf[num_core].min(numeric_only=True),
            "Max": cdf[num_core].max(numeric_only=True),
        }
    )
    print(mm.round(2).to_string())
    negs = {c: int((cdf[c] < 0).sum()) for c in num_core if (cdf[c] < 0).any()}
    if negs:
        print("  ! invalid negatives:", ", ".join(f"{c}={n}" for c, n in negs.items()))

    # --- Mode (this city's own dominant categories) ---
    print("\n[Mode]  (most frequent categories for this city)")
    for col in ["Province", "IslandGroup"] + CITY_CATEGORICAL:
        if col not in cdf.columns:
            continue
        vc = cdf[col].value_counts(dropna=True)
        if not vc.empty:
            print(f"  {col:<12}: {vc.index[0]!s:<18} (x{int(vc.iloc[0])})")

    # --- Correlation (needs enough rows) ---
    print("\n[Correlation]  (numeric vs. numeric)")
    if len(cdf) >= 3:
        corr = cdf[num_full].corr(numeric_only=True)
        print(corr.round(3).to_string())
    else:
        print("  skipped (need >= 3 records).")

    # --- Frequency distribution ---
    print("\n[Frequency distribution]  (counts per category)")
    for col in CITY_CATEGORICAL:
        if col not in cdf.columns:
            continue
        vc = cdf[col].value_counts(dropna=True)
        print(f"  {col}:")
        for idx, val in vc.items():
            print(f"    {idx!s:<14} {int(val)}")

    # --- Trend analysis (tables) ---
    print("\n[Trend analysis]  (avg by time period)")
    measures = [c for c in ["NumberOfVisitors", "AvgSpendingPHP"] if c in cdf.columns]
    for time_col in ["Year", "Season"]:
        if time_col not in cdf.columns:
            continue
        grouped = cdf.groupby(time_col)[measures].mean(numeric_only=True)
        print(f"  -- by {time_col} --")
        print(grouped.round(1).to_string().replace("\n", "\n  "))


# --------------------------------------------------------------------------- #
# Cross-city comparison
# --------------------------------------------------------------------------- #
def cross_city_summary(df):
    banner("CROSS-CITY COMPARISON  (rankings across all cities)")

    agg = df.groupby(CITY_COL).agg(
        Records=("NumberOfVisitors", "size"),
        AvgVisitors=("NumberOfVisitors", "mean"),
        MedVisitors=("NumberOfVisitors", "median"),
        AvgSpendPHP=("AvgSpendingPHP", "mean"),
        AvgStayDays=("AvgStayDays", "mean"),
        AvgSatisfaction=("SatisfactionRating", "mean"),
    ).round(2)

    print("\n--- Top 10 cities by average visitors ---")
    print(agg.sort_values("AvgVisitors", ascending=False).head(10).to_string())

    print("\n--- Top 10 cities by average spending (PHP) ---")
    print(agg.sort_values("AvgSpendPHP", ascending=False).head(10).to_string())

    print("\n--- Top 10 cities by average satisfaction ---")
    print(agg.sort_values("AvgSatisfaction", ascending=False).head(10).to_string())


def main():
    df = load_data(CSV_FILE)
    if CITY_COL not in df.columns:
        sys.exit(f"ERROR: column '{CITY_COL}' not found in the data.")

    cities = sorted(df[CITY_COL].dropna().unique())
    print(f"Loaded '{CSV_FILE}': {len(df)} rows, {len(cities)} cities.")

    # Per-city reports, ordered by number of records (busiest first).
    order = df[CITY_COL].value_counts().index
    for city in order:
        analyze_city(city, df[df[CITY_COL] == city])

    cross_city_summary(df)

    banner("DONE")


if __name__ == "__main__":
    main()
