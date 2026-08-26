"""Clean, standardize, and plot the Panel D aggregate crypto-market data."""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RAW_FILE = ROOT / "Panel_D_Data" / "Aggregate_Crypto_Market_Cap_Daily.csv"
CLEAN_FILE = (
    ROOT / "Panel_D_Data" / "Aggregate_Crypto_Market_Cap_Daily_Cleaned_Standardized.csv"
)
FIGURE_FILE = (
    ROOT / "Graphs_and_Diagrams" / "05C_Panel_D_Aggregate_Crypto_Market.png"
)

VALUE_COLUMNS = [
    "Aggregate_Crypto_Market_Cap_USD",
    "Aggregate_Crypto_Volume_24H_USD",
    "BTC_Dominance_Percent",
    "ETH_Dominance_Percent",
]


def interpolate_short_gaps(series: pd.Series, max_gap: int = 3) -> tuple[pd.Series, pd.Series]:
    """Time-interpolate only internal missing runs no longer than max_gap days."""
    missing = series.isna()
    groups = missing.ne(missing.shift()).cumsum()
    run_size = missing.groupby(groups).transform("sum")
    eligible = missing & run_size.le(max_gap)
    candidate = series.interpolate(method="time", limit_area="inside")
    cleaned = series.copy()
    cleaned.loc[eligible] = candidate.loc[eligible]
    return cleaned, eligible & candidate.notna()


def zscore(series: pd.Series) -> pd.Series:
    """Standardize available observations using the full-sample mean and SD."""
    return (series - series.mean()) / series.std(ddof=0)


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    data = raw.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce").dt.normalize()
    data = (
        data.dropna(subset=["Date"])
        .drop_duplicates(subset="Date", keep="last")
        .sort_values("Date")
        .set_index("Date")
    )
    data = data.reindex(pd.date_range(data.index.min(), data.index.max(), freq="D"))
    data.index.name = "Date"

    for column in VALUE_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    # Prices/sizes cannot be zero or negative; dominance must lie in (0, 100].
    invalid = pd.DataFrame(index=data.index)
    invalid["Market_Cap_Invalid"] = data["Aggregate_Crypto_Market_Cap_USD"].le(0)
    invalid["Volume_Invalid"] = data["Aggregate_Crypto_Volume_24H_USD"].le(0)
    for asset in ("BTC", "ETH"):
        column = f"{asset}_Dominance_Percent"
        invalid[f"{asset}_Dominance_Invalid"] = data[column].le(0) | data[column].gt(100)

    data.loc[invalid["Market_Cap_Invalid"], "Aggregate_Crypto_Market_Cap_USD"] = np.nan
    data.loc[invalid["Volume_Invalid"], "Aggregate_Crypto_Volume_24H_USD"] = np.nan
    for asset in ("BTC", "ETH"):
        data.loc[invalid[f"{asset}_Dominance_Invalid"], f"{asset}_Dominance_Percent"] = np.nan

    for column in VALUE_COLUMNS:
        data[column], filled = interpolate_short_gaps(data[column], max_gap=3)
        data[f"{column}_Short_Gap_Filled"] = filled.astype("int8")

    data["Log_Aggregate_Crypto_Market_Cap"] = np.log(
        data["Aggregate_Crypto_Market_Cap_USD"]
    )
    data["Log_Market_Cap_Z"] = zscore(data["Log_Aggregate_Crypto_Market_Cap"])
    data["BTC_Dominance_Z"] = zscore(data["BTC_Dominance_Percent"])
    data["ETH_Dominance_Z"] = zscore(data["ETH_Dominance_Percent"])

    for column in invalid.columns:
        data[column] = invalid[column].fillna(False).astype("int8")

    return data.reset_index()


def plot_data(data: pd.DataFrame) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(19, 9.5), dpi=160)

    ax.plot(
        data["Date"], data["Log_Market_Cap_Z"],
        color="#6A4C93", linewidth=2.2, label="Log aggregate market cap",
    )
    ax.plot(
        data["Date"], data["BTC_Dominance_Z"],
        color="#F7931A", linewidth=1.6, alpha=0.9, label="BTC dominance",
    )
    ax.plot(
        data["Date"], data["ETH_Dominance_Z"],
        color="#627EEA", linewidth=1.6, alpha=0.9, label="ETH dominance",
    )
    ax.axhline(0, color="#4B5563", linewidth=1, alpha=0.65)

    ax.set_title(
        "Panel D — Cleaned and Standardized Aggregate Crypto Market",
        fontsize=18, weight="bold", pad=15,
    )
    ax.set_ylabel("Standard deviations from each series mean (z-score)", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", ncol=3, frameon=True)
    ax.grid(True, alpha=0.22)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(
        0.01, 0.015,
        "Cleaning: invalid zero dominance values treated as missing; only internal gaps of up to "
        "3 days interpolated. Market cap is log-transformed before z-score standardization. "
        "ETH dominance begins when valid observations become available in October 2020.",
        fontsize=9, color="#4B5563",
    )
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    FIGURE_FILE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE_FILE, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    cleaned = clean_data(pd.read_csv(RAW_FILE))
    cleaned.to_csv(CLEAN_FILE, index=False)
    plot_data(cleaned)
    print(f"Saved {len(cleaned):,} cleaned daily rows to {CLEAN_FILE.relative_to(ROOT)}")
    print(f"Saved standardized diagram to {FIGURE_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
