redemption = pd.DataFrame({"Date": panel["Date"]})

for symbol in ("USDT", "USDC", "DAI"):
    peg_shortfall = (
        -price_output[f"{symbol}_Peg_Deviation_bps"]
    ).clip(lower=0)

    burn = (
        -panel[f"{symbol}_Net_Mint_Burn_Units"]
    ).clip(lower=0)

    prior_supply = panel[
        f"{symbol}_Circulating_Supply"
    ].shift(1)

    burn_intensity = (
        burn.div(prior_supply).mul(10_000)
    )

    redemption[f"{symbol}_Peg_Shortfall_bps"] = peg_shortfall
    redemption[f"{symbol}_Net_Burn_Intensity_bps"] = burn_intensity

    redemption[f"{symbol}_Redemption_Pressure_Index_bps"] = (
        peg_shortfall + burn_intensity
    )
# The formula is:
# Peg shortfall = max(0, −peg deviation in bps)

# Burn intensity = max(0, −daily supply change)
#                  ÷ previous-day supply × 10,000

# Redemption-pressure index = peg shortfall + burn intensity
# The supporting variables are constructed as follows:
# Daily net mint/burn
combined[f"{symbol}_Net_Mint_Burn_Units"] = combined[
    f"{symbol}_Circulating_Supply"
].diff()

# Peg deviation
price_output[f"{symbol}_Peg_Deviation_USD"] = (
    price_output[f"{symbol}_Price_USD"] - 1.0
)

price_output[f"{symbol}_Peg_Deviation_bps"] = (
    price_output[f"{symbol}_Peg_Deviation_USD"] * 10_000
)

def construct_sofr_ois_spreads() -> pd.DataFrame:
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
        .merge(
            ois_1m[["Date", "USD_1M_SOFR_OIS"]],
            on="Date",
            how="inner",
        )
        .merge(
            ois_3m[["Date", "USD_3M_SOFR_OIS"]],
            on="Date",
            how="inner",
        )
        .sort_values("Date")
        .reset_index(drop=True)
    )

    spreads["SOFR_minus_1M_OIS_bps"] = (
        spreads["SOFR"] - spreads["USD_1M_SOFR_OIS"]
    ) * 100

    spreads["SOFR_minus_3M_OIS_bps"] = (
        spreads["SOFR"] - spreads["USD_3M_SOFR_OIS"]
    ) * 100
#     1-month spread (bps) = (SOFR − 1-month SOFR OIS rate) × 100
# 3-month spread (bps) = (SOFR − 3-month SOFR OIS rate) × 100