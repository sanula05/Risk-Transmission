# Dataset Coverage and Frequency Report

Generated from the CSV files in the project on 31 July 2026. Date ranges are the minimum and maximum valid dates observed in each file. “Observations” is the number of unique timestamps/dates, except for the metadata-only availability file. Business/trading-daily series normally omit weekends and market holidays; calendar-daily series contain every calendar date.

## Executive summary

- The project contains **37 CSV datasets** across five panel folders.
- Frequencies represented are **5-minute, calendar daily, business/trading daily, monthly, and quarterly**.
- The earliest coverage is the monthly Global Policy Uncertainty series, beginning **January 1997**.
- The latest dated observations are **31 July 2026** in the aggregate crypto market-cap and funding-stress datasets.
- `Bank_5Y_CDS_Availability.csv` is a five-row metadata table and has no time range.

## Panel A — Stablecoin reserves, supply, prices, and redemption pressure

| Dataset | Frequency | From | To | Observations |
|---|---:|---:|---:|---:|
| `Aggregate_Stablecoin_Supply_Daily.csv` | Calendar daily | 2020-01-01 | 2026-07-28 | 2,401 |
| `Circle_USDC_Monthly_Asset_Composition_Disclosed.csv` | Monthly reports, irregular coverage | 2021-05 | 2023-01 | 8 report months |
| `Circle_USDC_Monthly_Reserve_Composition_From_May_2021.csv` | Monthly reports, with gaps | 2021-05 | 2026-06 | 41 report months |
| `Net_Mint_Burn_USDT_USDC_DAI_Daily.csv` | Calendar daily | 2020-01-01 | 2026-07-28 | 2,401 |
| `Redemption_Pressure_Index_Daily.csv` | Calendar daily | 2020-01-01 | 2026-07-28 | 2,401 |
| `Secondary_Prices_and_Peg_Deviations_Daily.csv` | Calendar daily | 2020-01-01 | 2026-07-28 | 2,401 |
| `Tether_Reserve_Composition_Coverage_From_2020.csv` | Quarterly coverage grid | 2020-03-31 | 2026-03-31 | 25 quarters |
| `Tether_Reserve_Composition_Quarterly.csv` | Quarterly reports, with gaps | 2021-06-30 | 2026-03-31 | 19 report dates |

## Panel B — Money-market funds, bank risk, and short-term funding rates

| Dataset | Frequency | From | To | Observations |
|---|---:|---:|---:|---:|
| `Bank_5Y_CDS_Availability.csv` | Metadata only | N/A | N/A | 5 banks |
| `Bank_5Y_CDS_Daily.csv` | Business/trading daily | 2020-01-02 | 2026-07-29 | 1,714 |
| `Exposed_Custodial_Bank_Equities_Daily.csv` | Trading daily | 2020-01-02 | 2026-07-29 | 1,651 |
| `Government_MMF_Net_Flows_Monthly.csv` | Monthly | 2020-01 | 2026-06 | 78 months |
| `Government_MMF_Total_AUM_Monthly.csv` | Monthly | 2020-01 | 2026-06 | 78 months |
| `KBW_Bank_Index_Daily.csv` | Trading daily | 2020-01-02 | 2026-07-29 | 1,651 |
| `MMF_by_cata.csv` | Monthly | 2011-01 | 2026-06 | 186 months |
| `SOFR.csv` | Business daily | 2020-07-29 | 2026-07-28 | 1,565 |
| `SOFR_OIS_Spreads_Daily.csv` | Business/trading daily | 2020-07-29 | 2026-07-27 | 1,495 |
| `TGCR_BGCR.csv` | Business daily; two rate types per date | 2022-01-03 | 2026-07-28 | 1,139 dates / 2,278 rows |
| `USD_1M_SOFR_OIS.csv` | Business/trading daily | 2020-01-02 | 2026-07-27 | 1,711 |
| `USD_3M_SOFR_OIS.csv` | Business/trading daily | 2020-01-02 | 2026-07-27 | 1,711 |
| `US_1M_Treasury_Bill_Yield.csv` | Business/trading daily | 2020-01-02 | 2026-07-27 | 1,642 |
| `US_3M_Treasury_Bill_Yield.csv` | Business/trading daily | 2020-01-02 | 2026-07-27 | 1,642 |

## Panel C — Crypto prices, returns, tokenised funds, and ETF flows

| Dataset | Frequency | From | To | Observations |
|---|---:|---:|---:|---:|
| `BTC_5_Minute_Prices.csv` | 5-minute intraday | 2026-05-30 00:00 UTC | 2026-07-28 15:35 UTC | 16,916 timestamps |
| `BTC_Daily_Returns.csv` | Calendar daily | 2020-01-01 | 2026-07-28 | 2,401 |
| `BUIDL_Market_cap.csv` | Calendar daily | 2024-03-20 | 2026-07-30 | 863 |
| `ETH_5_Minute_Prices.csv` | 5-minute intraday | 2026-05-30 00:00 UTC | 2026-07-28 15:35 UTC | 16,919 timestamps |
| `ETH_Daily_Returns.csv` | Calendar daily | 2020-01-01 | 2026-07-28 | 2,401 |
| `Spot_BTC_ETF_Net_Flows_Daily.csv` | Trading daily | 2024-01-11 | 2026-07-30 | 639 |
| `Spot_ETH_ETF_Net_Flows_Daily.csv` | Trading daily | 2024-07-23 | 2026-07-30 | 507 |

## Panel D — Market-wide controls and funding stress

| Dataset | Frequency | From | To | Observations |
|---|---:|---:|---:|---:|
| `Aggregate_Crypto_Market_Cap_Daily.csv` | Calendar daily | 2020-01-01 | 2026-07-31 | 2,404 |
| `Funding_Stress_Dummies_Daily.csv` | Calendar daily | 2020-01-01 | 2026-07-31 | 2,404 |
| `Global_Policy_Uncertainty_Data.csv` | Monthly | 1997-01 | 2026-06 | 354 unique months / 356 rows |
| `MOVE_Index_Daily.csv` | Business/trading daily | 2020-01-01 | 2026-07-27 | 1,645 |
| `VIX_Index_Daily.csv` | Trading daily | 2020-01-02 | 2026-07-28 | 1,650 |

## Panel E — Placebo short-duration sovereign assets

| Dataset | Frequency | From | To | Observations |
|---|---:|---:|---:|---:|
| `Euro_Area_Short_Bills_1M_3M_Daily.csv` | Business/trading daily | 2020-01-02 | 2026-07-30 | 1,689 |
| `Matched_NonReserve_UK_Short_Bills_1M_3M_Daily.csv` | Business/trading daily | 2020-01-02 | 2026-07-30 | 1,689 |
| `Placebo_Short_Duration_Assets_Daily.csv` | Business/trading daily | 2020-01-02 | 2026-07-30 | 1,689 |
| `Placebo_Short_Duration_Assets_LSEG_Raw.csv` | Business/trading daily | 2020-01-02 | 2026-07-30 | 1,689 |

## Data-quality and interpretation notes

1. The two Circle composition files are report datasets with multiple reserve-category rows per month. Their nominal frequency is monthly, but the observed month sequence contains gaps; the disclosed-only file has just eight distinct report months.
2. The Tether composition file similarly has multiple asset-category rows per report date and a missing quarter in its observed sequence. The separate coverage grid records all 25 quarters from March 2020 through March 2026, including dates for which disclosures were unavailable.
3. The two 5-minute crypto files have gaps substantially longer than five minutes, so “5-minute” describes the intended interval rather than uninterrupted coverage.
4. The Global Policy Uncertainty file has 356 rows but only 354 unique year-month combinations, indicating two duplicate month records that should be reviewed before time-series merges.
5. Different end dates across files mean a merged analysis should use an explicitly chosen common sample window or allow an unbalanced panel.

## Method

The report inspected every CSV under `Panel_A_Data` through `Panel_E_Data`, identified the relevant date or year/month field, parsed valid dates, and calculated minimum date, maximum date, and unique dated observations. Frequency classifications use both the file’s stated purpose/name and the observed spacing between consecutive dates.
