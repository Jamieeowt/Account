"""
Philippine Tourism Data — Interactive Console Menu
===================================================
Run:  python3 main_menu.py
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from tourism_analysis_per_city import *

# ─── Global Styles & Helpers ─────────────────────────────────────────────── #

plt.rcParams.update({'axes.titlesize': 13, 'axes.titleweight': 'bold'})
FMT_NUM = mticker.FuncFormatter(lambda x, _: f"{int(x):,}")
FMT_PHP = mticker.FuncFormatter(lambda x, _: f"₱{int(x):,}")

def banner(t): print(f"\n{'='*68}\n  {t}\n{'='*68}")
def section(t): print(f"\n{'-'*68}\n  {t}\n{'-'*68}")
def pause(): input("\n  [Press ENTER to continue...]")

def get_df(state):
    if (df := state.get("df")) is None:
        print("\n  ⚠  Load the data first (Option 1)."); pause()
    return df

def pick_city(df):
    cities = sorted(df[CITY_COL].dropna().unique())
    banner("SELECT A CITY")
    for i, c in enumerate(cities, 1): print(f"  {i:>3}. {c}")
    while True:
        try:
            if 1 <= (n := int(input("\n  Enter city number: "))) <= len(cities):
                return cities[n - 1]
        except ValueError: pass
        print("  Invalid — try again.")

def show_fig():
    plt.tight_layout()
    plt.show()

# ─── Menus ───────────────────────────────────────────────────────────────── #

def menu_load(state):
    banner("LOAD DATA SET")
    df = load_data()
    state["df"], removed = clean_data(df)
    print(f"  Cleaned rows : {len(state['df'])} ({removed} removed)")
    print(f"  Cities       : {state['df'][CITY_COL].nunique()}")
    pause()

def menu_display(state):
    if (df := get_df(state)) is None: return
    banner("CLEANED DATA — FIRST 20 ROWS")
    pd.set_option("display.max_columns", None, "display.width", 160)
    print(df.head(20).to_string(index=False))
    section("DATA SUMMARY")
    print(df.describe(include="all").round(2).to_string())
    pause()

def menu_compute(state):
    if (df := get_df(state)) is None: return
    
    # Map choices directly to the functions that calculate them
    funcs = {
        "1": ("Mean & Median", lambda c: city_mean_median(c).to_string()),
        "2": ("Mode", lambda c: city_mode(c).to_string(index=False)),
        "3": ("Standard Deviation", lambda c: city_std(c).to_string()),
        "4": ("Min & Max", lambda c: city_minmax(c).to_string()),
        "5": ("Correlation", lambda c: city_correlation(c)[1] or city_correlation(c)[0].to_string()),
        "6": ("Trend Analysis", lambda c: "\n".join(f"\n  — by {p} —\n{t.to_string()}" for p, t in city_trend(c).items())),
        "7": ("Frequencies", lambda c: "\n".join(f"\n  {col}:\n" + "\n".join(f"    {k:<18} {int(v)}" for k, v in vc.items()) for col, vc in city_frequency(c).items()))
    }
    
    while True:
        banner("PERFORM COMPUTATIONS")
        for k, (label, _) in funcs.items(): print(f"  {k}. {label}")
        print("  0. ← Back")
        
        if (choice := input("\n  Option: ").strip()) == "0": return
        if choice not in funcs: continue
        
        city = pick_city(df)
        section(f"{funcs[choice][0].upper()}  —  {city}")
        print(funcs[choice][1](df[df[CITY_COL] == city].copy()))
        pause()

def menu_charts(state):
    if (df := get_df(state)) is None: return
    charts = [
        "Tourists by Month/Season", "Avg Spending (Top 15)", "Most Visited Cities",
        "Visitors by Year", "Visitors by Month", "Season Share (Pie)", 
        "Island Group Share (Pie)", "Accommodation (Pie)", "Avg Spending Dist.", 
        "Avg Stay Dist.", "Stay vs Spending (Scatter)", "Satisfaction vs Spending (Scatter)"
    ]
    
    while True:
        banner("GENERATE CHARTS")
        for i, lbl in enumerate(charts, 1): print(f"  {i:>2}. {lbl}")
        print("   0. ← Back")
        
        choice = input("\n  Option: ").strip()
        if choice == "0": return
        
        match choice:
            case "1":
                city = pick_city(df)
                cdf = df[df[CITY_COL] == city]
                fig, axes = plt.subplots(1, 2, figsize=(14, 5))
                fig.suptitle(f"Tourist Counts — {city}", fontsize=14, fontweight="bold")
                mo = cdf.groupby("Month")["NumberOfVisitors"].sum().reindex([m for m in MONTH_ORDER if m in cdf["Month"].unique()])
                axes[0].bar(mo.index, mo.values, color="#1f77b4")
                axes[0].set(title="By Month", xlabel="Month", ylabel="Total Visitors")
                axes[0].tick_params(axis="x", rotation=45)
                
                se = cdf.groupby("Season")["NumberOfVisitors"].sum()
                axes[1].bar(se.index, se.values, color=["#2ca02c","#d62728"])
                axes[1].set(title="By Season", xlabel="Season")
                for ax in axes: ax.yaxis.set_major_formatter(FMT_NUM)

            case "2" | "3":
                col, fmt, clr, title = ("AvgSpendingPHP", FMT_PHP, "#ff7f0e", "Average Spending") if choice == "2" else ("NumberOfVisitors", FMT_NUM, "#9467bd", "Most Visited Cities")
                agg = df.groupby(CITY_COL)[col].mean().nlargest(15).sort_values() if choice == "2" else df.groupby(CITY_COL)[col].sum().nlargest(15).sort_values()
                fig, ax = plt.subplots(figsize=(12, 7))
                bars = ax.barh(agg.index, agg.values, color=clr)
                ax.set(title=f"{title} (Top 15)", xlabel=title)
                ax.xaxis.set_major_formatter(fmt)
                for b in bars: ax.text(b.get_width(), b.get_y() + b.get_height()/2, f" {int(b.get_width()):,}", va="center", fontsize=8)

            case "4" | "5":
                col = "Year" if choice == "4" else "Month"
                agg = df.groupby(col)["NumberOfVisitors"].sum()
                if choice == "5": agg = agg.reindex([m for m in MONTH_ORDER if m in agg.index])
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(agg.index, agg.values, marker="o", color="#1f77b4" if choice == "4" else "#2ca02c", lw=2.5)
                ax.set(title=f"Total Visitors by {col}", xlabel=col, ylabel="Total Visitors")
                ax.yaxis.set_major_formatter(FMT_NUM)
                ax.grid(axis="y", ls="--", alpha=0.5)

            case "6" | "7" | "8":
                col = {"6": "Season", "7": "IslandGroup", "8": "Accommodation"}[choice]
                data = df.groupby(col)["NumberOfVisitors"].sum() if choice != "8" else df[col].value_counts()
                fig, ax = plt.subplots(figsize=(7, 7))
                ax.pie(data.values, labels=data.index, autopct="%1.1f%%", wedgeprops={"edgecolor":"white","linewidth":2}, textprops={"fontsize":11})
                ax.set_title(f"Share by {col}")

            case "9" | "10":
                col, fmt, lbl = ("AvgSpendingPHP", FMT_PHP, "Spending (PHP)") if choice == "9" else ("AvgStayDays", FMT_NUM, "Stay (Days)")
                data = df[col].dropna()
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.hist(data, bins=20, color="#e76f51" if choice == "9" else "#457b9d", edgecolor="white")
                ax.set(title=f"Distribution of {lbl}", xlabel=lbl, ylabel="Frequency")
                if choice == "9": ax.xaxis.set_major_formatter(fmt)
                ax.axvline(data.mean(), color="navy", ls="--", label="Mean")
                ax.axvline(data.median(), color="green", ls="--", label="Median")
                ax.legend()

            case "11" | "12":
                y_col = "AvgSpendingPHP" if choice == "11" else "SatisfactionRating"
                x_col = "AvgStayDays" if choice == "11" else "AvgSpendingPHP"
                grp = "IslandGroup" if choice == "11" else "Season"
                sub = df[[x_col, y_col, grp]].dropna()
                
                fig, ax = plt.subplots(figsize=(10, 6))
                for g, gdf in sub.groupby(grp): ax.scatter(gdf[x_col], gdf[y_col], label=g, alpha=0.65)
                ax.set(title=f"{y_col} vs {x_col}", xlabel=x_col, ylabel=y_col)
                ax.legend(title=grp); ax.grid(ls="--", alpha=0.4)
                
            case _: continue
        
        if choice in [str(i) for i in range(1, 13)]: show_fig()

def menu_summary(state):
    if (df := get_df(state)) is None: return
    banner("OUTPUT — SUMMARIZED RESULTS")
    agg = cross_city_summary(df)
    for title, col in [("Visitors", "AvgVisitors"), ("Spending", "AvgSpendPHP"), ("Satisfaction", "AvgSatisfaction"), ("Stay", "AvgStayDays")]:
        section(f"Top 10 by {title}")
        print(agg.sort_values(col, ascending=False).head(10).to_string())
    pause()

def main():
    state = {}
    menus = {"1": ("Load Data", menu_load), "2": ("Display Data", menu_display), "3": ("Compute", menu_compute), "4": ("Charts", menu_charts), "5": ("Summary", menu_summary)}
    while True:
        banner("PHILIPPINE TOURISM DATA ANALYSIS")
        for k, (lbl, _) in menus.items(): print(f"  {k}. {lbl}")
        print("  0. Exit")
        
        if (choice := input("\n  Option: ").strip()) == "0": sys.exit(0)
        if choice in menus: menus[choice][1](state)

if __name__ == "__main__": main()