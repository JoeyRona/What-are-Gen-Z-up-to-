"""
clean.py - turn every raw file in data/raw/ into a tidy, analysis-ready CSV in data/processed/.

Rules:
- Raw files are never edited. Every correction happens here, with a comment explaining why.
- Each cleaner is its own function, so it can be tested and re-run on its own.
- Files that haven't been downloaded yet are skipped with a message, not a crash.

Run from the project root:  python src/clean.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def read_raw(filename: str, **kwargs) -> pd.DataFrame:
    """
    Read a raw file whether it's a real CSV or an Excel workbook saved with a .csv name.

    The Google Trends and CSO downloads in data/raw/ are .xlsx files renamed to .csv,
    so pd.read_csv fails on them. Excel files are zip archives and always start with
    the bytes 'PK', which is how we tell the two apart.
    """
    path = RAW / filename
    with open(path, "rb") as f:
        is_excel = f.read(2) == b"PK"
    if is_excel:
        return pd.read_excel(path, engine="openpyxl", **kwargs)
    return pd.read_csv(path, **kwargs)

# Known errors in the DIGI 2026 report (documented in data/DATA_DICTIONARY.md).
# Format: (county, year): (value_as_printed, corrected_value, reason)
COUNTY_CORRECTIONS = {
    ("Clare", 2023): (
        176,
        259,
        "Typo in source: sits between 277 (2022) and 265 (2024); "
        "national total of 6,563 implies 259.",
    ),
}


# --------------------------------------------------------------------------- #
# Pubs
# --------------------------------------------------------------------------- #
def clean_pubs_national() -> pd.DataFrame:
    df = pd.read_csv(RAW / "pubs_national_by_year.csv")
    df = df[["year", "pub_licences"]].astype(int).sort_values("year")

    # Recalculate change from the data itself instead of trusting the typed column.
    df["annual_change"] = df["pub_licences"].diff()
    df["pct_change"] = (df["pub_licences"].pct_change() * 100).round(2)
    df["pct_of_2005"] = (df["pub_licences"] / df["pub_licences"].iloc[0] * 100).round(1)
    return df.reset_index(drop=True)


def clean_pubs_county() -> pd.DataFrame:
    wide = pd.read_csv(RAW / "pubs_by_county.csv")
    wide["county"] = wide["county"].str.strip().str.title()

    # Wide (one column per year) -> long (one row per county per year).
    long = wide.melt(id_vars="county", var_name="year", value_name="pubs")
    long["year"] = long["year"].str.replace("pubs_", "", regex=False).astype(int)
    long["pubs"] = long["pubs"].astype(int)
    long["corrected"] = False

    for (county, year), (printed, fixed, _reason) in COUNTY_CORRECTIONS.items():
        mask = (long["county"] == county) & (long["year"] == year)
        assert long.loc[mask, "pubs"].item() == printed, f"{county} {year} not as expected"
        long.loc[mask, ["pubs", "corrected"]] = [fixed, True]

    long["region"] = long["county"].map(lambda c: "Dublin" if c == "Dublin" else "Outside Dublin")
    return long.sort_values(["county", "year"]).reset_index(drop=True)


def county_summary(long: pd.DataFrame) -> pd.DataFrame:
    """One row per county: 2005 vs 2025 and % lost. Feeds the county ranking chart."""
    pivot = long.pivot(index="county", columns="year", values="pubs")
    out = pd.DataFrame({
        "pubs_2005": pivot[2005],
        "pubs_2025": pivot[2025],
    })
    out["pubs_lost"] = out["pubs_2005"] - out["pubs_2025"]
    out["pct_lost"] = (out["pubs_lost"] / out["pubs_2005"] * 100).round(1)
    return out.sort_values("pct_lost", ascending=False).reset_index()


def check_county_totals(long: pd.DataFrame, national: pd.DataFrame) -> pd.DataFrame:
    """Compare county sums with the national figure for each year after corrections."""
    sums = long.groupby("year")["pubs"].sum().rename("county_sum")
    nat = national.set_index("year")["pub_licences"].rename("national")
    check = pd.concat([sums, nat], axis=1, join="inner")
    check["difference"] = check["county_sum"] - check["national"]
    return check.reset_index()


# --------------------------------------------------------------------------- #
# Minimum wage
# --------------------------------------------------------------------------- #
def clean_min_wage(start="2015-01", end=None) -> pd.DataFrame:
    """Step changes -> one row per month, so it can be joined to monthly price data."""
    df = pd.read_csv(RAW / "min_wage.csv", parse_dates=["effective_date"])
    df = df.sort_values("effective_date")

    end = end or pd.Timestamp.today().strftime("%Y-%m")
    months = pd.period_range(start, end, freq="M")
    monthly = pd.DataFrame({"month": months})
    monthly["month_start"] = monthly["month"].dt.to_timestamp()

    # For each month, take the most recent rate that had taken effect by the 1st of that month.
    # Note: Feb 2020's rise (1 Feb) therefore applies from February, not January.
    monthly = pd.merge_asof(
        monthly, df[["effective_date", "hourly_rate_eur"]],
        left_on="month_start", right_on="effective_date", direction="backward",
    )
    monthly["month"] = monthly["month"].astype(str)
    return monthly[["month", "hourly_rate_eur"]]


# --------------------------------------------------------------------------- #
# Dating apps
# --------------------------------------------------------------------------- #
def clean_dating_apps() -> pd.DataFrame:
    df = pd.read_csv(RAW / "dating_app_payers.csv")
    df["app"] = df["app"].str.strip()
    df = df.sort_values(["app", "year"])
    # Change within each app only: definitions differ between companies.
    df["pct_change"] = (df.groupby("app")["paying_users_millions"].pct_change() * 100).round(1)
    return df[["year", "app", "paying_users_millions", "pct_change", "metric"]].reset_index(drop=True)


# --------------------------------------------------------------------------- #
# CSO Consumer Price Index
# --------------------------------------------------------------------------- #
CPI_FILE = "cpi-alcohol_tobacco.csv"


def clean_cpi() -> pd.DataFrame:
    """
    CSO PxStat table CPM01, 'Alcoholic beverages and tobacco', base Dec 2023 = 100.
    Columns in the raw file: Statistic Label, Month, Commodity Group, UNIT, VALUE.

    Limitation: this group combines alcohol *and* tobacco, and doesn't split pub
    prices from off-licence prices. Documented in DATA_DICTIONARY.md.
    """
    df = read_raw(CPI_FILE)
    out = df.rename(columns={
        "Month": "month",
        "Commodity Group": "series",
        "VALUE": "index_value",
        "UNIT": "base",
    })[["month", "series", "index_value", "base"]]

    # PxStat months look like '2019 November' -> '2019-11'
    out["month"] = pd.to_datetime(out["month"], format="%Y %B").dt.strftime("%Y-%m")
    out["index_value"] = pd.to_numeric(out["index_value"], errors="coerce")
    out = out.dropna(subset=["index_value"]).sort_values(["series", "month"])

    # Year-on-year inflation for this group: compare each month with 12 months earlier.
    out["yoy_pct"] = (out.groupby("series")["index_value"].pct_change(12) * 100).round(2)
    return out.reset_index(drop=True)


# --------------------------------------------------------------------------- #
# Google Trends
# --------------------------------------------------------------------------- #
# file -> (group, term). Each file was exported with ONE search term, Ireland,
# monthly, Nov 2015 - Nov 2025.
TRENDS_FILES = {
    "trends_going_pub.csv": ("going_out", "pub"),
    "trends_nightclub.csv": ("going_out", "nightclub"),
    "app_tinder_trends.csv": ("apps", "tinder"),
    "app_trends_hinge.csv": ("apps", "hinge"),
    "app_trends_bumble.csv": ("apps", "bumble"),
}
BASE_YEAR = "2016"  # first full calendar year in the exports


def read_trends(filename: str) -> pd.DataFrame:
    """One Trends export -> columns: month, interest."""
    df = read_raw(filename)
    df = df.rename(columns={df.columns[0]: "month", df.columns[1]: "interest"})
    df["month"] = pd.to_datetime(df["month"]).dt.strftime("%Y-%m")
    # Trends uses '<1' for very low interest -> 0.5
    df["interest"] = pd.to_numeric(df["interest"].replace("<1", 0.5))
    return df[["month", "interest"]]


def clean_trends() -> pd.DataFrame:
    """
    Combine the single-term Trends exports into one long table.

    Important: each file was exported on its own, so each is scaled 0-100 *within itself*.
    A value of 50 for Tinder and 50 for Hinge does NOT mean equal search volume.
    To make terms comparable we index each one to its own 2016 average (= 100):
        index_2016 = 200 -> searched twice as much as in 2016
        index_2016 = 50  -> searched half as much as in 2016
    This compares *change over time* between terms, not their absolute popularity.
    """
    frames = []
    for filename, (group, term) in TRENDS_FILES.items():
        df = read_trends(filename)
        base = df.loc[df["month"].str.startswith(BASE_YEAR), "interest"].mean()
        df["index_2016"] = (df["interest"] / base * 100).round(1)
        df["group"], df["term"] = group, term
        frames.append(df)

    out = pd.concat(frames, ignore_index=True)
    return out[["month", "group", "term", "interest", "index_2016"]]


# --------------------------------------------------------------------------- #
# Run everything
# --------------------------------------------------------------------------- #
def save(df: pd.DataFrame, name: str) -> None:
    df.to_csv(PROCESSED / name, index=False)
    print(f"  saved {name:<28} {len(df):>5} rows")


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    print("Cleaning raw data...")

    national = clean_pubs_national()
    save(national, "pubs_national.csv")

    county = clean_pubs_county()
    save(county, "pubs_county_long.csv")
    save(county_summary(county), "pubs_county_summary.csv")

    check = check_county_totals(county, national)
    print("\n  County totals vs national (after corrections):")
    print(check.to_string(index=False).replace("\n", "\n  "), "\n")

    save(clean_min_wage(), "min_wage_monthly.csv")
    save(clean_dating_apps(), "dating_apps.csv")

    if (RAW / CPI_FILE).exists():
        save(clean_cpi(), "cpi.csv")
    else:
        print(f"  skipped {CPI_FILE} (not downloaded yet)")

    missing = [f for f in TRENDS_FILES if not (RAW / f).exists()]
    if missing:
        print(f"  skipped Google Trends (missing: {', '.join(missing)})")
    else:
        save(clean_trends(), "trends.csv")

    print("Done.")


if __name__ == "__main__":
    main()
