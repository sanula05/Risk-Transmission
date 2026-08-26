"""Create a static conceptual dashboard of directional risk transmission.

The values are illustrative placeholders, not econometric estimates.
Rows are risk givers and columns are risk receivers.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


OUTPUT = Path(__file__).resolve().parent / "directional_risk_network_concept.png"

# Labels mirror the variables contained in Panels A-C (givers) and B-D (receivers).
givers = [
    "Stablecoin net\nmint / burn",
    "Stablecoin peg\ndeviation",
    "Redemption-pressure\nindex",
    "BTC / ETH\nreturns",
    "Spot crypto ETF\nnet flows",
    "Tokenized-fund\nmarket cap",
]

receivers = [
    "1M / 3M\nT-bill yields",
    "SOFR–OIS\nspread",
    "TGCR / BGCR\nrepo",
    "Government MMF\nAUM / flows",
    "Bank 5Y CDS /\nfunding",
    "Bank equities /\nKBW index",
]

# Placeholder intensity: 0 = no visible channel, 5 = strongest proposed channel.
bad_news = np.array(
    [
        [5, 4, 4, 5, 4, 3],
        [3, 4, 3, 3, 5, 4],
        [4, 5, 4, 4, 5, 4],
        [2, 3, 2, 2, 4, 5],
        [2, 3, 2, 3, 3, 4],
        [4, 4, 4, 3, 3, 2],
    ]
)

good_news = np.array(
    [
        [4, 3, 3, 4, 2, 2],
        [2, 4, 3, 2, 4, 3],
        [3, 4, 3, 3, 4, 3],
        [1, 2, 1, 2, 3, 5],
        [1, 2, 1, 2, 2, 4],
        [4, 3, 3, 3, 2, 2],
    ]
)


def annotate_heatmap(axis, values):
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            score = values[row, column]
            text_color = "white" if score >= 4 else "#1f2933"
            axis.text(
                column,
                row,
                str(score),
                ha="center",
                va="center",
                color=text_color,
                fontsize=11,
                fontweight="bold",
            )


red_scale = LinearSegmentedColormap.from_list(
    "bad_news", ["#fff7ed", "#fdba74", "#dc2626", "#7f1d1d"]
)
green_scale = LinearSegmentedColormap.from_list(
    "good_news", ["#f0fdf4", "#86efac", "#16a34a", "#14532d"]
)

fig, axes = plt.subplots(1, 2, figsize=(18, 9), constrained_layout=True)

for axis, values, title, subtitle, colour_map in [
    (
        axes[0],
        bad_news,
        "Bad news: redemption-shock transmission",
        "Stress passed from crypto/stablecoin rails to funding markets",
        red_scale,
    ),
    (
        axes[1],
        good_news,
        "Good news: stabilization transmission",
        "Confidence, inflows and liquidity support passed to receivers",
        green_scale,
    ),
]:
    image = axis.imshow(values, cmap=colour_map, vmin=0, vmax=5, aspect="auto")
    annotate_heatmap(axis, values)
    axis.set_xticks(np.arange(len(receivers)), labels=receivers)
    axis.set_yticks(np.arange(len(givers)), labels=givers)
    axis.tick_params(axis="x", rotation=35, labelsize=9)
    axis.tick_params(axis="y", labelsize=10)
    axis.set_xlabel("RISK RECEIVER  →", fontsize=11, fontweight="bold", labelpad=13)
    axis.set_ylabel("RISK GIVER  →", fontsize=11, fontweight="bold", labelpad=13)
    axis.set_title(title, fontsize=14, fontweight="bold", pad=28)
    axis.text(
        0.5,
        1.015,
        subtitle,
        transform=axis.transAxes,
        ha="center",
        va="bottom",
        fontsize=10,
        color="#52606d",
    )
    axis.set_xticks(np.arange(-0.5, len(receivers), 1), minor=True)
    axis.set_yticks(np.arange(-0.5, len(givers), 1), minor=True)
    axis.grid(which="minor", color="white", linestyle="-", linewidth=2)
    axis.tick_params(which="minor", bottom=False, left=False)

colour_bar = fig.colorbar(image, ax=axes, location="bottom", shrink=0.55, pad=0.08)
colour_bar.set_ticks(range(6))
colour_bar.set_label(
    "Illustrative directional transmission intensity: 0 = none, 5 = strongest",
    fontsize=10,
)

fig.suptitle(
    "Directional Risk Network Dashboard",
    fontsize=20,
    fontweight="bold",
    y=1.04,
)
fig.text(
    0.5,
    -0.035,
    "Conceptual placeholders only — not estimated coefficients or causal results. "
    "Read each cell as: row giver → column receiver.",
    ha="center",
    fontsize=11,
    fontweight="bold",
    color="#334e68",
)

fig.savefig(OUTPUT, dpi=220, bbox_inches="tight", facecolor="white")
print(f"Saved {OUTPUT}")

