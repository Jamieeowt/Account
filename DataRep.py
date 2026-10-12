    """
    Philippine Tourism Data — Interactive Console Menu
    ===================================================
    Run:  python3 main_menu.py
    """

    import sys
    import math
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker

    from tourism_analysis_per_city import (
        load_data, clean_data,
        city_mean_median, city_mode, city_std, city_minmax,
        city_correlation, city_trend, city_frequency,
        cross_city_summary, CITY_COL, MONTH_ORDER,
    )

    # ─── helpers ─────────────────────────────────────────────────────────────── #

    DIVIDER = "=" * 68
    THIN    = "-" * 68

    def banner(title):
        print(f"\n{DIVIDER}")
        print(f"  {title}")
        print(DIVIDER)

    def section(title):
        print(f"\n{THIN}")
        print(f"  {title}")
        print(THIN)

    def pause():
        input("\n  [Press ENTER to continue...]")

    def pick_city(df):
        cities = sorted(df[CITY_COL].dropna().unique())
        banner("SELECT A CITY")
        for i, c in enumerate(cities, 1):
            print(f"  {i:>3}. {c}")
        while True:
            try:
                n = int(input("\n  Enter city number: "))
                if 1 <= n <= len(cities):
                    return cities[n - 1]
            except ValueError:
                pass
            print("  Invalid — try again.")

    def show_fig():
        """Opens the plot in an interactive window instead of saving."""
        plt.tight_layout()
        plt.show()

    # ─── 1. Load Data ────────────────────────────────────────────────────────── #

    def menu_load(state):
        banner("LOAD DATA SET")
        df = load_data()
        df_clean, removed = clean_data(df)
        state["df_raw"]   = df
        state["df"]       = df_clean
        print(f"  File         : philippines_tourism_data.csv")
        print(f"  Raw rows     : {len(df)}")
        print(f"  Cleaned rows : {len(df_clean)}  ({removed} removed — negatives / duplicates)")
        print(f"  Columns      : {len(df.columns)}")
        print(f"  Cities       : {df_clean[CITY_COL].nunique()}")
        print(f"  Years        : {sorted(df_clean['Year'].dropna().unique())}")
        pause()

    # ─── 2. Display Cleaned Data ─────────────────────────────────────────────── #

    def menu_display(state):
        df = state.get("df")
        if df is None:
            print("\n  ⚠  Load the data first (Option 1).")
            pause(); return
        banner("CLEANED DATA — FIRST 20 ROWS")
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 160)
        print(df.head(20).to_string(index=False))
        section("DATA SUMMARY")
        print(df.describe(include="all").round(2).to_string())
        pause()

    # ─── 3. Computations ─────────────────────────────────────────────────────── #

    CALC_MENU = {
        "1": ("Mean & Median",             "mean_median"),
        "2": ("Mode",                      "mode"),
        "3": ("Standard Deviation",        "std"),
        "4": ("Minimum & Maximum Values",  "minmax"),
        "5": ("Correlation Analysis",      "correlation"),
        "6": ("Trend Analysis",            "trend"),
        "7": ("Frequency Distributions",   "frequency"),
        "8": ("← Back to Main Menu",       "back"),
    }

    def menu_compute(state):
        df = state.get("df")
        if df is None:
            print("\n  ⚠  Load the data first (Option 1).")
            pause(); return

        while True:
            banner("PERFORM COMPUTATIONS — SELECT CALCULATION")
            for k, (label, _) in CALC_MENU.items():
                print(f"  {k}. {label}")

            choice = input("\n  Option: ").strip()
            if choice not in CALC_MENU:
                print("  Invalid option."); continue

            _, action = CALC_MENU[choice]
            if action == "back":
                return

            city = pick_city(df)
            cdf  = df[df[CITY_COL] == city].copy()
            section(f"{CALC_MENU[choice][0].upper()}  —  {city}  ({len(cdf)} records)")

            if action == "mean_median":
                print(city_mean_median(cdf).to_string())

            elif action == "mode":
                result = city_mode(cdf)
                print(result.to_string(index=False))

            elif action == "std":
                print(city_std(cdf).to_string())

            elif action == "minmax":
                print(city_minmax(cdf).to_string())

            elif action == "correlation":
                corr, msg = city_correlation(cdf)
                if msg:
                    print(f"  {msg}")
                else:
                    print(corr.to_string())

            elif action == "trend":
                trends = city_trend(cdf)
                for period, tbl in trends.items():
                    print(f"\n  — by {period} —")
                    print(tbl.to_string())

            elif action == "frequency":
                freqs = city_frequency(cdf)
                for col, vc in freqs.items():
                    print(f"\n  {col}:")
                    for idx, val in vc.items():
                        print(f"    {str(idx):<18} {int(val)}")

            pause()

    # ─── 4. Charts ───────────────────────────────────────────────────────────── #

    CHART_MENU = {
        "1": "Bar Graph — Tourists by Month/Season (per city)",
        "2": "Bar Graph — Average Spending by Destination (Top 15)",
        "3": "Bar Graph — Most Visited Cities",
        "4": "Line Graph — Visitors by Year",
        "5": "Line Graph — Visitors by Month (Jan–Dec)",
        "6": "Pie Chart — Season Share (Dry vs Wet)",
        "7": "Pie Chart — Island Group Share",
        "8": "Pie Chart — Accommodation Types",
        "9": "Histogram — Average Spending Distribution",
        "10": "Histogram — Average Stay Days Distribution",
        "11": "Scatter Plot — Stay Days vs Spending",
        "12": "Scatter Plot — Satisfaction vs Spending",
        "0": "← Back to Main Menu",
    }

    def menu_charts(state):
        df = state.get("df")
        if df is None:
            print("\n  ⚠  Load the data first (Option 1).")
            pause(); return

        while True:
            banner("GENERATE CHARTS")
            for k, label in CHART_MENU.items():
                print(f"  {k:>2}. {label}")

            choice = input("\n  Option: ").strip()
            if choice == "0":
                return
            if choice not in CHART_MENU:
                print("  Invalid option."); continue

            # ── Chart 1: Bar — tourists per month/season for a city ──────────
            if choice == "1":
                city = pick_city(df)
                cdf  = df[df[CITY_COL] == city]
                fig, axes = plt.subplots(1, 2, figsize=(14, 5))
                fig.suptitle(f"Tourist Counts — {city}", fontsize=14, fontweight="bold")

                # by month
                mo = cdf.groupby("Month")["NumberOfVisitors"].sum()
                present = [m for m in MONTH_ORDER if m in mo.index]
                mo = mo.reindex(present)
                axes[0].bar(mo.index, mo.values, color="#1f77b4")
                axes[0].set_title("By Month"); axes[0].set_xlabel("Month")
                axes[0].set_ylabel("Total Visitors")
                axes[0].tick_params(axis="x", rotation=45)
                axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

                # by season
                se = cdf.groupby("Season")["NumberOfVisitors"].sum()
                axes[1].bar(se.index, se.values, color=["#2ca02c","#d62728"])
                axes[1].set_title("By Season"); axes[1].set_xlabel("Season")
                axes[1].set_ylabel("Total Visitors")
                axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

                show_fig()

            # ── Chart 2: Bar — avg spending by destination (top 15) ──────────
            elif choice == "2":
                agg = df.groupby(CITY_COL)["AvgSpendingPHP"].mean().nlargest(15).sort_values()
                fig, ax = plt.subplots(figsize=(12, 7))
                bars = ax.barh(agg.index, agg.values, color="#ff7f0e")
                ax.set_title("Average Spending per Tourist by Destination (Top 15)",
                            fontsize=13, fontweight="bold")
                ax.set_xlabel("Average Spending (PHP)")
                ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₱{int(x):,}"))
                for bar in bars:
                    w = bar.get_width()
                    ax.text(w + 200, bar.get_y() + bar.get_height()/2,
                            f"₱{int(w):,}", va="center", fontsize=8)
                show_fig()

            # ── Chart 3: Bar — amost visited cities ───────────────────────────
            elif choice == "3":
                agg = df.groupby(CITY_COL)["NumberOfVisitors"].sum().nlargest(15).sort_values()
                fig, ax = plt.subplots(figsize=(12, 7))
                bars = ax.barh(agg.index, agg.values, color="#9467bd")
                ax.set_title("Most Visited Cities — Total Visitors (Top 15)",
                            fontsize=13, fontweight="bold")
                ax.set_xlabel("Total Visitors")
                ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
                for bar in bars:
                    w = bar.get_width()
                    ax.text(w + 500, bar.get_y() + bar.get_height()/2,
                            f"{int(w):,}", va="center", fontsize=8)
                show_fig()

            # ── Chart 4: Line — visitors by year ─────────────────────────────
            elif choice == "4":
                agg = df.groupby("Year")["NumberOfVisitors"].sum()
                fig, ax = plt.subplots(figsize=(9, 5))
                ax.plot(agg.index, agg.values, marker="o", linewidth=2.5,
                        color="#1f77b4", markersize=8)
                for x, y in zip(agg.index, agg.values):
                    ax.annotate(f"{int(y):,}", (x, y), textcoords="offset points",
                                xytext=(0, 10), ha="center", fontsize=9)
                ax.set_title("Total Number of Visitors per Year", fontsize=13, fontweight="bold")
                ax.set_xlabel("Year"); ax.set_ylabel("Total Visitors")
                ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
                ax.set_xticks(agg.index)
                ax.grid(axis="y", linestyle="--", alpha=0.5)
                show_fig()

            # ── Chart 5: Line — visitors by month (Jan–Dec) ──────────────────
            elif choice == "5":
                mo = df.groupby("Month")["NumberOfVisitors"].sum()
                present = [m for m in MONTH_ORDER if m in mo.index]
                mo = mo.reindex(present)
                fig, ax = plt.subplots(figsize=(12, 5))
                ax.plot(mo.index, mo.values, marker="o", linewidth=2.5,
                        color="#2ca02c", markersize=8)
                for x, y in zip(mo.index, mo.values):
                    ax.annotate(f"{int(y):,}", (x, y), textcoords="offset points",
                                xytext=(0, 10), ha="center", fontsize=8)
                ax.set_title("Total Visitors by Month (All Years)", fontsize=13, fontweight="bold")
                ax.set_xlabel("Month"); ax.set_ylabel("Total Visitors")
                ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
                ax.tick_params(axis="x", rotation=30)
                ax.grid(axis="y", linestyle="--", alpha=0.5)
                show_fig()

            # ── Chart 6: Pie — season share ───────────────────────────────────
            elif choice == "6":
                se = df.groupby("Season")["NumberOfVisitors"].sum()
                fig, ax = plt.subplots(figsize=(7, 7))
                wedge_props = {"edgecolor": "white", "linewidth": 2}
                ax.pie(se.values, labels=se.index, autopct="%1.1f%%",
                    colors=["#f4a261","#457b9d"],
                    wedgeprops=wedge_props, startangle=140,
                    textprops={"fontsize": 13})
                ax.set_title("Visitors by Season (Dry vs Wet)",
                            fontsize=13, fontweight="bold")
                show_fig()

            # ── Chart 7: Pie — island group share ────────────────────────────
            elif choice == "7":
                ig = df.groupby("IslandGroup")["NumberOfVisitors"].sum()
                fig, ax = plt.subplots(figsize=(7, 7))
                ax.pie(ig.values, labels=ig.index, autopct="%1.1f%%",
                    colors=["#e9c46a","#2a9d8f","#e76f51"],
                    wedgeprops={"edgecolor":"white","linewidth":2},
                    startangle=90, textprops={"fontsize":13})
                ax.set_title("Visitors by Island Group", fontsize=13, fontweight="bold")
                show_fig()

            # ── Chart 8: Pie — accommodation ─────────────────────────────────
            elif choice == "8":
                ac = df["Accommodation"].value_counts(dropna=True)
                colors = ["#264653","#2a9d8f","#e9c46a","#f4a261","#e76f51","#6d6875"]
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(ac.values, labels=ac.index, autopct="%1.1f%%",
                    colors=colors[:len(ac)],
                    wedgeprops={"edgecolor":"white","linewidth":2},
                    startangle=120, textprops={"fontsize":11})
                ax.set_title("Market Share by Accommodation Type",
                            fontsize=13, fontweight="bold")
                show_fig()

            # ── Chart 9: Histogram — avg spending ────────────────────────────
            elif choice == "9":
                data = df["AvgSpendingPHP"].dropna()
                fig, ax = plt.subplots(figsize=(10, 5))
                n, bins, patches = ax.hist(data, bins=20, color="#e76f51",
                                        edgecolor="white", linewidth=0.8)
                ax.set_title("Distribution of Average Spending per Tourist (PHP)",
                            fontsize=13, fontweight="bold")
                ax.set_xlabel("Average Spending (PHP)")
                ax.set_ylabel("Frequency")
                ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₱{int(x):,}"))
                ax.grid(axis="y", linestyle="--", alpha=0.5)
                # annotate mean & median
                ax.axvline(data.mean(),   color="navy",   linestyle="--", label=f"Mean ₱{data.mean():,.0f}")
                ax.axvline(data.median(), color="green",  linestyle="--", label=f"Median ₱{data.median():,.0f}")
                ax.legend()
                show_fig()

            # ── Chart 10: Histogram — avg stay days ──────────────────────────
            elif choice == "10":
                data = df["AvgStayDays"].dropna()
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.hist(data, bins=15, color="#457b9d", edgecolor="white", linewidth=0.8)
                ax.set_title("Distribution of Average Stay Duration (Days)",
                            fontsize=13, fontweight="bold")
                ax.set_xlabel("Average Stay (Days)")
                ax.set_ylabel("Frequency")
                ax.axvline(data.mean(),   color="navy",  linestyle="--", label=f"Mean {data.mean():.1f} days")
                ax.axvline(data.median(), color="green", linestyle="--", label=f"Median {data.median():.1f} days")
                ax.legend()
                ax.grid(axis="y", linestyle="--", alpha=0.5)
                show_fig()

            # ── Chart 11: Scatter — stay days vs spending ─────────────────────
            elif choice == "11":
                sub = df[["AvgStayDays","AvgSpendingPHP","IslandGroup"]].dropna()
                colors_map = {"Luzon":"#1f77b4","Visayas":"#2ca02c","Mindanao":"#d62728"}
                fig, ax = plt.subplots(figsize=(10, 6))
                for grp, gdf in sub.groupby("IslandGroup"):
                    ax.scatter(gdf["AvgStayDays"], gdf["AvgSpendingPHP"],
                            label=grp, alpha=0.65, s=50,
                            color=colors_map.get(grp, "gray"))
                ax.set_title("Stay Duration vs. Average Spending",
                            fontsize=13, fontweight="bold")
                ax.set_xlabel("Average Stay Days")
                ax.set_ylabel("Average Spending (PHP)")
                ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₱{int(x):,}"))
                ax.legend(title="Island Group")
                ax.grid(linestyle="--", alpha=0.4)
                # trend line
                m, b = pd.Series(sub["AvgStayDays"]).cov(sub["AvgSpendingPHP"]) / sub["AvgStayDays"].var(), 0
                xs = pd.Series([sub["AvgStayDays"].min(), sub["AvgStayDays"].max()])
                m = (sub["AvgSpendingPHP"].cov(sub["AvgStayDays"])) / (sub["AvgStayDays"].var())
                b = sub["AvgSpendingPHP"].mean() - m * sub["AvgStayDays"].mean()
                ax.plot(xs, m * xs + b, "k--", linewidth=1.2, label="Trend")
                ax.legend(title="Island Group")
                show_fig()

            # ── Chart 12: Scatter — satisfaction vs spending ──────────────────
            elif choice == "12":
                sub = df[["SatisfactionRating","AvgSpendingPHP","Season"]].dropna()
                colors_map = {"Dry":"#f4a261","Wet":"#457b9d"}
                fig, ax = plt.subplots(figsize=(10, 6))
                for grp, gdf in sub.groupby("Season"):
                    ax.scatter(gdf["AvgSpendingPHP"], gdf["SatisfactionRating"],
                            label=grp, alpha=0.65, s=50,
                            color=colors_map.get(grp, "gray"))
                ax.set_title("Satisfaction Rating vs. Average Spending",
                            fontsize=13, fontweight="bold")
                ax.set_xlabel("Average Spending (PHP)")
                ax.set_ylabel("Satisfaction Rating (1–5)")
                ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₱{int(x):,}"))
                ax.set_ylim(0, 5.5)
                ax.legend(title="Season")
                ax.grid(linestyle="--", alpha=0.4)
                # trend line
                m = sub["SatisfactionRating"].cov(sub["AvgSpendingPHP"]) / sub["AvgSpendingPHP"].var()
                b = sub["SatisfactionRating"].mean() - m * sub["AvgSpendingPHP"].mean()
                xs = pd.Series([sub["AvgSpendingPHP"].min(), sub["AvgSpendingPHP"].max()])
                ax.plot(xs, m * xs + b, "k--", linewidth=1.2, label="Trend")
                ax.legend(title="Season")
                show_fig()

            else:
                print("  Not yet implemented.")

            pause()

    # ─── 5. Summarized Results ───────────────────────────────────────────────── #

    def menu_summary(state):
        df = state.get("df")
        if df is None:
            print("\n  ⚠  Load the data first (Option 1).")
            pause(); return

        banner("OUTPUT — SUMMARIZED RESULTS")
        agg = cross_city_summary(df)

        section("Top 10 Cities by Average Visitors")
        print(agg.sort_values("AvgVisitors", ascending=False).head(10).to_string())

        section("Top 10 Cities by Average Spending (PHP)")
        print(agg.sort_values("AvgSpendPHP", ascending=False).head(10).to_string())

        section("Top 10 Cities by Average Satisfaction Rating")
        print(agg.sort_values("AvgSatisfaction", ascending=False).head(10).to_string())

        section("Top 10 Cities by Average Stay Duration (Days)")
        print(agg.sort_values("AvgStayDays", ascending=False).head(10).to_string())

        section("Overall Dataset Summary")
        print(f"  Total records   : {len(df):,}")
        print(f"  Total cities    : {df[CITY_COL].nunique()}")
        print(f"  Total visitors  : {df['NumberOfVisitors'].sum():,.0f}")
        print(f"  Mean spending   : ₱{df['AvgSpendingPHP'].mean():,.2f}")
        print(f"  Mean stay       : {df['AvgStayDays'].mean():.2f} days")
        print(f"  Mean rating     : {df['SatisfactionRating'].mean():.2f} / 5.0")
        pause()

    # ─── Main menu ───────────────────────────────────────────────────────────── #

    MAIN_MENU = {
        "1": ("Load Data Set",              menu_load),
        "2": ("Display Cleaned Data",       menu_display),
        "3": ("Perform Computations",       menu_compute),
        "4": ("Generate Charts",            menu_charts),
        "5": ("Output Summarized Results",  menu_summary),
        "0": ("Exit",                       None),
    }

    def main():
        state = {}
        while True:
            banner("PHILIPPINE TOURISM DATA ANALYSIS")
            for k, (label, _) in MAIN_MENU.items():
                print(f"  {k}. {label}")

            choice = input("\n  Option: ").strip()

            if choice == "0":
                print("\n  Goodbye!\n")
                sys.exit(0)

            if choice not in MAIN_MENU:
                print("  Invalid option — try again.")
                continue

            _, handler = MAIN_MENU[choice]
            handler(state)

    if __name__ == "__main__":
        main()