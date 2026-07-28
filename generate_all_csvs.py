"""Regenerate the CSV datasets used by data_forma.ipynb.

Sources
-------
Panel A: DeFiLlama stablecoin API
Panel B: LSEG Workspace Data Library and FRED
Panel C: Yahoo Finance through yfinance

Examples
--------
    python generate_all_csvs.py --panels a
    python generate_all_csvs.py --panels b
    python generate_all_csvs.py --panels c
    python generate_all_csvs.py --panels a c
    python generate_all_csvs.py --panels all

Panel B requires LSEG Workspace to be open and signed in. No LSEG username,
password, or application key is stored in this file.
"""

from __future__ import annotations

import argparse
from datetime import date
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parent
PANEL_A_FOLDER = ROOT / "Panel_A_Data"
PANEL_B_FOLDER = ROOT / "Panel_B_Data"
PANEL_C_FOLDER = ROOT / "Panel_C_Data"

DEFILLAMA_CATALOG_URL = (
    "https://stablecoins.llama.fi/stablecoins?includePrices=true"
)
DEFILLAMA_HISTORY_URL = (
    "https://stablecoins.llama.fi/stablecoincharts/all?stablecoin={stablecoin_id}"
)
FRED_SOFR_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def _today_string() -> str:
    return date.today().isoformat()


def _request_json(url: str) -> Any:
    response = requests.get(
        url,
        timeout=60,
        headers={"User-Agent": "Risk-Transmission-Research/1.0"},
    )
    response.raise_for_status()
    return response.json()


def _pegged_usd(value: Any) -> float:
    """Extract the pegged-USD number from a DeFiLlama value object."""
    if isinstance(value, dict):
        value = value.get("peggedUSD")
    return pd.to_numeric(value, errors="coerce")


def _find_stablecoin_ids() -> dict[str, str]:
    catalog = _request_json(DEFILLAMA_CATALOG_URL)
    assets = catalog.get("peggedAssets", catalog)
    wanted = {"USDT", "USDC", "DAI"}
    found: dict[str, str] = {}

    for asset in assets:
        symbol = str(asset.get("symbol", "")).upper()
        if symbol in wanted and symbol not in found:
            found[symbol] = str(asset["id"])

    missing = wanted.difference(found)
    if missing:
        raise ValueError(
            "DeFiLlama catalogue did not contain: " + ", ".join(sorted(missing))
        )
    return found


def _defillama_coin_history(symbol: str, stablecoin_id: str) -> pd.DataFrame:
    payload = _request_json(
        DEFILLAMA_HISTORY_URL.format(stablecoin_id=stablecoin_id)
    )
    records = payload if isinstance(payload, list) else payload.get("tokens", [])
    if not records:
        raise ValueError(f"DeFiLlama returned no history for {symbol}")

    raw = pd.DataFrame(records)
    required = {"date", "totalCirculating", "totalCirculatingUSD"}
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(
            f"DeFiLlama history for {symbol} is missing columns: {sorted(missing)}"
        )

    result = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                pd.to_numeric(raw["date"], errors="coerce"),
                unit="s",
                utc=True,
            ).dt.normalize(),
            f"{symbol}_Circulating_Supply": raw["totalCirculating"].map(
                _pegged_usd
            ),
            f"{symbol}_Market_Cap_USD": raw["totalCirculatingUSD"].map(
                _pegged_usd
            ),
        }
    )
    result = result.dropna(subset=["Date"]).sort_values("Date")
    result = result.groupby("Date", as_index=False).last()
    supply = result[f"{symbol}_Circulating_Supply"].replace(0, pd.NA)
    result[f"{symbol}_Price_USD"] = result[f"{symbol}_Market_Cap_USD"] / supply
    return result


def generate_panel_a(start: str = "2020-01-01", end: str | None = None) -> None:
    """Create the four Panel A stablecoin CSV files from DeFiLlama."""
    PANEL_A_FOLDER.mkdir(parents=True, exist_ok=True)
    end = end or _today_string()
    stablecoin_ids = _find_stablecoin_ids()

    histories = [
        _defillama_coin_history(symbol, stablecoin_ids[symbol])
        for symbol in ("USDT", "USDC", "DAI")
    ]
    combined = histories[0]
    for history in histories[1:]:
        combined = combined.merge(history, on="Date", how="outer")

    # Reindex before calculating flows so the first retained date can use the
    # previous day's supply. Forward filling converts sparse updates to daily data.
    full_dates = pd.date_range(
        combined["Date"].min(), pd.Timestamp(end, tz="UTC"), freq="D"
    )
    combined = (
        combined.set_index("Date")
        .reindex(full_dates)
        .sort_index()
        .ffill()
        .rename_axis("Date")
        .reset_index()
    )

    for symbol in ("USDT", "USDC", "DAI"):
        combined[f"{symbol}_Net_Mint_Burn_Units"] = combined[
            f"{symbol}_Circulating_Supply"
        ].diff()

    start_ts = pd.Timestamp(start, tz="UTC")
    end_ts = pd.Timestamp(end, tz="UTC")
    panel = combined.loc[combined["Date"].between(start_ts, end_ts)].copy()

    supply_columns = [
        "USDT_Circulating_Supply",
        "USDC_Circulating_Supply",
        "DAI_Circulating_Supply",
    ]
    aggregate_supply = panel[["Date", *supply_columns]].copy()
    aggregate_supply["Aggregate_Stablecoin_Supply"] = aggregate_supply[
        supply_columns
    ].sum(axis=1, min_count=len(supply_columns))
    aggregate_supply.to_csv(
        PANEL_A_FOLDER / "Aggregate_Stablecoin_Supply_Daily.csv", index=False
    )

    flow_columns = [
        "USDT_Net_Mint_Burn_Units",
        "USDC_Net_Mint_Burn_Units",
        "DAI_Net_Mint_Burn_Units",
    ]
    panel[["Date", *flow_columns]].to_csv(
        PANEL_A_FOLDER / "Net_Mint_Burn_USDT_USDC_DAI_Daily.csv", index=False
    )

    price_output = panel[
        ["Date", "USDT_Price_USD", "USDC_Price_USD", "DAI_Price_USD"]
    ].copy()
    for symbol in ("USDT", "USDC", "DAI"):
        price_output[f"{symbol}_Peg_Deviation_USD"] = (
            price_output[f"{symbol}_Price_USD"] - 1.0
        )
        price_output[f"{symbol}_Peg_Deviation_bps"] = (
            price_output[f"{symbol}_Peg_Deviation_USD"] * 10_000
        )

    ordered_price_columns = ["Date"]
    ordered_price_columns += [f"{s}_Price_USD" for s in ("USDT", "USDC", "DAI")]
    for symbol in ("USDT", "USDC", "DAI"):
        ordered_price_columns += [
            f"{symbol}_Peg_Deviation_USD",
            f"{symbol}_Peg_Deviation_bps",
        ]
    price_output = price_output[ordered_price_columns]
    price_output.to_csv(
        PANEL_A_FOLDER / "Secondary_Prices_and_Peg_Deviations_Daily.csv",
        index=False,
    )

    redemption = pd.DataFrame({"Date": panel["Date"]})
    for symbol in ("USDT", "USDC", "DAI"):
        peg_shortfall = (-price_output[f"{symbol}_Peg_Deviation_bps"]).clip(
            lower=0
        )
        burn = (-panel[f"{symbol}_Net_Mint_Burn_Units"]).clip(lower=0)
        prior_supply = panel[f"{symbol}_Circulating_Supply"].shift(1)
        burn_intensity = burn.div(prior_supply).mul(10_000)

        redemption[f"{symbol}_Peg_Shortfall_bps"] = peg_shortfall
        redemption[f"{symbol}_Net_Burn_Intensity_bps"] = burn_intensity
        redemption[f"{symbol}_Redemption_Pressure_Index_bps"] = (
            peg_shortfall + burn_intensity
        )

    redemption.to_csv(
        PANEL_A_FOLDER / "Redemption_Pressure_Index_Daily.csv", index=False
    )
    print("Panel A: saved 4 CSV files to", PANEL_A_FOLDER)


LSEG_SERIES = (
    (
        "US1MT=RR",
        "MID_PRICE",
        "US_1M_Treasury_Bill_Yield",
        "US_1M_Treasury_Bill_Yield.csv",
    ),
    (
        "US3MT=RR",
        "MID_PRICE",
        "US_3M_Treasury_Bill_Yield",
        "US_3M_Treasury_Bill_Yield.csv",
    ),
    (
        "USDSROIS1M=",
        "MID_PRICE",
        "USD_1M_SOFR_OIS",
        "USD_1M_SOFR_OIS.csv",
    ),
    (
        "USDSROIS3M=",
        "MID_PRICE",
        "USD_3M_SOFR_OIS",
        "USD_3M_SOFR_OIS.csv",
    ),
)


def _history_value_series(history: pd.DataFrame, field: str) -> pd.Series:
    """Normalize the different single-RIC column layouts returned by LSEG."""
    if history.empty:
        raise ValueError("LSEG returned an empty history DataFrame")

    if isinstance(history.columns, pd.MultiIndex):
        matching = [
            column
            for column in history.columns
            if field in {str(level) for level in column}
        ]
        column = matching[0] if matching else history.columns[0]
    elif field in history.columns:
        column = field
    else:
        column = history.columns[0]

    return pd.to_numeric(history[column], errors="coerce")


def _download_lseg_series(
    ld: Any,
    ric: str,
    field: str,
    output_column: str,
    filename: str,
    start: str,
    end: str,
) -> None:
    history = ld.get_history(
        universe=ric,
        fields=[field],
        interval="1D",
        start=start,
        end=end,
    )
    values = _history_value_series(history, field)
    output = pd.DataFrame(
        {
            "Date": pd.to_datetime(history.index, utc=True),
            "RIC": ric,
            "LSEG_Field": field,
            output_column: values.to_numpy(),
        }
    ).dropna(subset=[output_column])
    output = output.sort_values("Date").drop_duplicates("Date", keep="last")
    output.to_csv(PANEL_B_FOLDER / filename, index=False)
    print(f"  saved {len(output):,} rows to {filename}")


def download_sofr_from_fred(
    start: str = "2020-01-01", end: str | None = None
) -> pd.DataFrame:
    """Download the daily SOFR series from FRED without requiring an API key."""
    end = end or _today_string()
    response = requests.get(
        FRED_SOFR_URL,
        params={"id": "SOFR", "cosd": start, "coed": end},
        timeout=60,
        headers={"User-Agent": "Risk-Transmission-Research/1.0"},
    )
    response.raise_for_status()
    sofr = pd.read_csv(StringIO(response.text))
    sofr.columns = ["observation_date", "SOFR"]
    sofr["observation_date"] = pd.to_datetime(
        sofr["observation_date"], errors="coerce"
    )
    sofr["SOFR"] = pd.to_numeric(sofr["SOFR"], errors="coerce")
    sofr = sofr.dropna(subset=["observation_date", "SOFR"])
    sofr = sofr.sort_values("observation_date").drop_duplicates(
        "observation_date", keep="last"
    )
    sofr.to_csv(PANEL_B_FOLDER / "SOFR.csv", index=False)
    return sofr


def construct_sofr_ois_spreads() -> pd.DataFrame:
    """Construct SOFR minus the 1-month and 3-month OIS rates in basis points."""
    sofr = pd.read_csv(PANEL_B_FOLDER / "SOFR.csv")
    ois_1m = pd.read_csv(PANEL_B_FOLDER / "USD_1M_SOFR_OIS.csv")
    ois_3m = pd.read_csv(PANEL_B_FOLDER / "USD_3M_SOFR_OIS.csv")

    sofr = sofr.rename(columns={"observation_date": "Date"})
    for frame in (sofr, ois_1m, ois_3m):
        frame["Date"] = (
            pd.to_datetime(frame["Date"], utc=True)
            .dt.tz_localize(None)
            .dt.normalize()
        )

    spreads = (
        sofr[["Date", "SOFR"]]
        .merge(ois_1m[["Date", "USD_1M_SOFR_OIS"]], on="Date", how="inner")
        .merge(ois_3m[["Date", "USD_3M_SOFR_OIS"]], on="Date", how="inner")
        .sort_values("Date")
        .reset_index(drop=True)
    )
    spreads["SOFR_minus_1M_OIS_bps"] = (
        spreads["SOFR"] - spreads["USD_1M_SOFR_OIS"]
    ) * 100
    spreads["SOFR_minus_3M_OIS_bps"] = (
        spreads["SOFR"] - spreads["USD_3M_SOFR_OIS"]
    ) * 100
    spreads.to_csv(PANEL_B_FOLDER / "SOFR_OIS_Spreads_Daily.csv", index=False)
    return spreads


def generate_panel_b(start: str = "2020-01-01", end: str | None = None) -> None:
    """Create Panel B LSEG/FRED files and construct the SOFR-OIS spreads."""
    try:
        import lseg.data as ld
    except ImportError as exc:
        raise RuntimeError(
            "Panel B requires the lseg-data package and an entitled Workspace login."
        ) from exc

    PANEL_B_FOLDER.mkdir(parents=True, exist_ok=True)
    end = end or _today_string()

    print("Opening the active LSEG Workspace session...")
    ld.open_session()
    try:
        for ric, field, output_column, filename in LSEG_SERIES:
            print(f"Downloading {output_column} ({ric})...")
            _download_lseg_series(
                ld, ric, field, output_column, filename, start, end
            )
    finally:
        ld.close_session()

    sofr = download_sofr_from_fred(start, end)
    spreads = construct_sofr_ois_spreads()
    print(f"  saved {len(sofr):,} rows to SOFR.csv")
    print(f"  saved {len(spreads):,} rows to SOFR_OIS_Spreads_Daily.csv")
    print("Panel B: saved 6 CSV files to", PANEL_B_FOLDER)


def _yahoo_download(ticker: str, **request: Any) -> pd.DataFrame:
    import yfinance as yf

    try:
        data = yf.download(
            ticker,
            progress=False,
            threads=False,
            multi_level_index=False,
            **request,
        )
    except TypeError:
        # Compatibility with older yfinance versions lacking multi_level_index.
        data = yf.download(ticker, progress=False, threads=False, **request)

    if data.empty:
        raise ValueError(f"Yahoo Finance returned no data for {ticker}")
    if isinstance(data.columns, pd.MultiIndex):
        price_fields = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}
        first_level = {str(value) for value in data.columns.get_level_values(0)}
        data.columns = data.columns.get_level_values(
            0 if price_fields.intersection(first_level) else -1
        )
    return data


def _create_daily_crypto_file(symbol: str, ticker: str, start: str) -> None:
    prices = _yahoo_download(
        ticker,
        start=start,
        interval="1d",
        auto_adjust=False,
        actions=False,
    )
    prices.index = pd.to_datetime(prices.index, utc=True).tz_convert(None).normalize()
    close_column = "Adj Close" if "Adj Close" in prices.columns else "Close"
    output = pd.DataFrame(
        {
            "Date": prices.index,
            f"{symbol}_Adjusted_Close_USD": prices[close_column].to_numpy(),
        }
    )
    output[f"{symbol}_Daily_Return"] = output[
        f"{symbol}_Adjusted_Close_USD"
    ].pct_change()
    output[f"{symbol}_Daily_Return_Percent"] = (
        output[f"{symbol}_Daily_Return"] * 100
    )
    output.to_csv(PANEL_C_FOLDER / f"{symbol}_Daily_Returns.csv", index=False)
    print(f"  saved {len(output):,} rows to {symbol}_Daily_Returns.csv")


def _create_intraday_crypto_file(symbol: str, ticker: str) -> None:
    # yfinance documents that intraday data cannot extend beyond the last 60 days.
    prices = _yahoo_download(
        ticker,
        period="60d",
        interval="5m",
        auto_adjust=False,
        actions=False,
        prepost=False,
    )
    prices.index = pd.to_datetime(prices.index, utc=True)
    prices.index.name = "Datetime_UTC"
    columns = [
        column
        for column in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        if column in prices.columns
    ]
    output = prices[columns].reset_index()
    output.to_csv(PANEL_C_FOLDER / f"{symbol}_5_Minute_Prices.csv", index=False)
    print(f"  saved {len(output):,} rows to {symbol}_5_Minute_Prices.csv")


def generate_panel_c(start: str = "2020-01-01") -> None:
    """Create four Panel C BTC/ETH files through yfinance."""
    PANEL_C_FOLDER.mkdir(parents=True, exist_ok=True)
    for symbol, ticker in (("BTC", "BTC-USD"), ("ETH", "ETH-USD")):
        _create_daily_crypto_file(symbol, ticker, start)
        _create_intraday_crypto_file(symbol, ticker)
    print("Panel C: saved 4 CSV files to", PANEL_C_FOLDER)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regenerate Panel A, B, and C research CSV files."
    )
    parser.add_argument(
        "--panels",
        nargs="+",
        choices=("a", "b", "c", "all"),
        default=("all",),
        help="Panels to generate. Examples: --panels a c or --panels all",
    )
    parser.add_argument(
        "--start",
        default="2020-01-01",
        help="Daily-data start date in YYYY-MM-DD format (default: 2020-01-01)",
    )
    parser.add_argument(
        "--end",
        default=None,
        help="Panel A/B end date in YYYY-MM-DD format (default: today)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    selected = {"a", "b", "c"} if "all" in args.panels else set(args.panels)

    if "a" in selected:
        generate_panel_a(args.start, args.end)
    if "b" in selected:
        generate_panel_b(args.start, args.end)
    if "c" in selected:
        generate_panel_c(args.start)


if __name__ == "__main__":
    main()
