"""
Philippine Tourism Data — Per-City Statistical Analysis
=======================================================
Module used by main_menu.py. Provides:
  - load_data()
  - clean_data()
  - city_mean_median()
  - city_mode()
  - city_std()
  - city_minmax()
  - city_correlation()
  - city_trend()
  - city_frequency()
  - cross_city_summary()
"""

import sys
from pathlib import Path

import pandas as pd

CSV_FILE = "philippines_tourism_data.csv"
CITY_COL = "Destination"

NUMERIC_FULL = ["NumberOfVisitors", "AvgSpendingPHP", "AvgStayDays", "SatisfactionRating"]
NUMERIC_CORE = ["NumberOfVisitors", "AvgSpendingPHP", "AvgStayDays"]
CITY_CATEGORICAL = ["Month", "Season"]

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def load_data(path=CSV_FILE):
    if not Path(path).exists():
        sys.exit(f"ERROR: could not find '{path}'.")
    df = pd.read_csv(path)
    for col in NUMERIC_FULL:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Normalize destination names
    df[CITY_COL] = df[CITY_COL].str.strip().str.title()
    return df


def clean_data(df):
    """Return cleaned copy and summary of changes."""
    original = len(df)
    df = df.copy()
    df[CITY_COL] = df[CITY_COL].str.strip().str.title()
    for col in NUMERIC_CORE:
        if col in df.columns:
            df = df[~(df[col] < 0)]
    df = df.drop_duplicates()
    removed = original - len(df)
    return df, removed


# ─── Per-city computations ───────────────────────────────────────────────── #

def city_mean_median(cdf):
    cols = [c for c in NUMERIC_FULL if c in cdf.columns]
    result = pd.DataFrame({
        "Mean":   cdf[cols].mean(numeric_only=True),
        "Median": cdf[cols].median(numeric_only=True),
    })
    return result.round(2)


def city_mode(cdf):
    rows = []
    for col in ["Province", "IslandGroup"] + CITY_CATEGORICAL + ["Accommodation", "TouristOrigin", "VisitPurpose"]:
        if col not in cdf.columns:
            continue
        vc = cdf[col].value_counts(dropna=True)
        if not vc.empty:
            rows.append({"Category": col, "Mode": str(vc.index[0]), "Count": int(vc.iloc[0])})
    return pd.DataFrame(rows)


def city_std(cdf):
    cols = [c for c in NUMERIC_CORE if c in cdf.columns]
    result = pd.DataFrame({
        "Mean":   cdf[cols].mean(numeric_only=True),
        "StdDev": cdf[cols].std(numeric_only=True),
    })
    return result.round(2)


def city_minmax(cdf):
    cols = [c for c in NUMERIC_CORE if c in cdf.columns]
    result = pd.DataFrame({
        "Min": cdf[cols].min(numeric_only=True),
        "Max": cdf[cols].max(numeric_only=True),
    })
    return result.round(2)


def city_correlation(cdf):
    cols = [c for c in NUMERIC_FULL if c in cdf.columns]
    if len(cdf) < 3:
        return None, "Skipped — need >= 3 records."
    return cdf[cols].corr(numeric_only=True).round(3), None


def city_trend(cdf):
    measures = [c for c in ["NumberOfVisitors", "AvgSpendingPHP"] if c in cdf.columns]
    results = {}
    for time_col in ["Year", "Season", "Month"]:
        if time_col not in cdf.columns:
            continue
        grouped = cdf.groupby(time_col)[measures].mean(numeric_only=True)
        if time_col == "Month":
            present = [m for m in MONTH_ORDER if m in grouped.index]
            if present:
                grouped = grouped.reindex(present)
        results[time_col] = grouped.round(1)
    return results


def city_frequency(cdf):
    results = {}
    for col in CITY_CATEGORICAL + ["Accommodation", "VisitPurpose", "IslandGroup"]:
        if col not in cdf.columns:
            continue
        vc = cdf[col].value_counts(dropna=True)
        results[col] = vc
    return results


# ─── Cross-city summary ──────────────────────────────────────────────────── #

def cross_city_summary(df):
    agg = df.groupby(CITY_COL).agg(
        Records        =("NumberOfVisitors", "size"),
        AvgVisitors    =("NumberOfVisitors", "mean"),
        MedVisitors    =("NumberOfVisitors", "median"),
        AvgSpendPHP    =("AvgSpendingPHP",  "mean"),
        AvgStayDays    =("AvgStayDays",     "mean"),
        AvgSatisfaction=("SatisfactionRating","mean"),
    ).round(2)
    return agg
