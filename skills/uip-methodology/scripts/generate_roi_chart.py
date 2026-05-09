#!/usr/bin/env python3
"""Generate an ROI payback chart from an architecture review document.

Usage:
    uv run uipath/uipath-rpa-design/scripts/generate_roi_chart.py docs/arch-review.md
    uv run uipath/uipath-rpa-design/scripts/generate_roi_chart.py docs/arch-review.md --out docs/roi-chart.png
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_REGION_RE = re.compile(
    r"<!--\s*#region\s+roi_summary\s*-->(.+?)<!--\s*#endregion\s+roi_summary\s*-->",
    re.DOTALL,
)
_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
_NUM_CLEAN = re.compile(r"[€$£,\s]")
_MD_BOLD = re.compile(r"\*{1,2}|_{1,2}")

_BLUE = "#00338D"
_RED = "#D40511"
_GREEN = "#2E7D32"
_GRAY = "#9E9E9E"
__all__ = ["main"]


def _extract_roi(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    m = _REGION_RE.search(text)
    if not m:
        sys.exit(f"ERROR: no <!-- #region roi_summary --> block found in {path}")
    result: dict[str, str] = {}
    for row in _ROW_RE.finditer(m.group(1)):
        item = _MD_BOLD.sub("", row.group(1).strip())
        value = _MD_BOLD.sub("", row.group(2).strip())
        if item.lower() in ("item", "---", ""):
            continue
        key = item.lower().replace(" ", "_")
        if value and value != "[TBD]":
            result[key] = value
    return result


def _num(d: dict[str, str], key: str) -> float | None:
    raw = d.get(key, "")
    if not raw or raw == "[TBD]":
        return None
    try:
        return float(_NUM_CLEAN.sub("", raw))
    except ValueError:
        return None


def _require(d: dict[str, str], *keys: str) -> list[float]:
    vals: list[float] = []
    missing: list[str] = []
    for k in keys:
        v = _num(d, k)
        if v is None:
            missing.append(k)
        else:
            vals.append(v)
    if missing:
        sys.exit(
            "ERROR: required ROI fields are [TBD] or missing — fill in the arch-review first:\n"
            + "\n".join(f"  • {k}" for k in missing)
        )
    return vals


def _build_figure(roi: dict[str, str]):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    build_cost, monthly_net, year1, year3 = _require(
        roi, "build_cost", "monthly_net_saving", "year_1_net_benefit", "year_3_net_benefit"
    )

    payback_m = _num(roi, "payback_months") or (build_cost / monthly_net if monthly_net else 0)

    horizon = max(36, int(payback_m) + 12)
    months = list(range(0, horizon + 1))
    cum = [-build_cost + m * monthly_net for m in months]

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Payback Curve", "Net Benefit"),
        column_widths=[0.62, 0.38],
        horizontal_spacing=0.10,
    )

    neg_m = [m for m, v in zip(months, cum, strict=False) if v <= 0]
    neg_v = [v for v in cum if v <= 0]
    pos_m = [m for m, v in zip(months, cum, strict=False) if v >= 0]
    pos_v = [v for v in cum if v >= 0]

    if neg_m:
        fig.add_trace(
            go.Scatter(
                x=neg_m,
                y=neg_v,
                fill="tozeroy",
                fillcolor="rgba(212,5,17,0.10)",
                line=dict(color=_RED, width=0),
                name="Cost zone",
                hoverinfo="skip",
            ),
            row=1,
            col=1,
        )

    if pos_m:
        fig.add_trace(
            go.Scatter(
                x=pos_m,
                y=pos_v,
                fill="tozeroy",
                fillcolor="rgba(46,125,50,0.12)",
                line=dict(color=_GREEN, width=0),
                name="Benefit zone",
                hoverinfo="skip",
            ),
            row=1,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=months,
            y=cum,
            line=dict(color=_BLUE, width=2.5),
            name="Cumulative value",
            hovertemplate="Month %{x}: €%{y:,.0f}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_hline(y=0, line=dict(color=_GRAY, dash="dot", width=1), row=1, col=1)
    fig.add_vline(x=payback_m, line=dict(color=_RED, dash="dash", width=1.5), row=1, col=1)
    fig.add_annotation(
        x=payback_m,
        y=0,
        text=f"Break-even<br>mo. {payback_m:.1f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor=_RED,
        font=dict(color=_RED, size=10),
        bgcolor="white",
        bordercolor=_RED,
        borderwidth=1,
        ax=28,
        ay=-36,
        row=1,
        col=1,
    )

    for yr, label in ((12, "Y1"), (24, "Y2"), (36, "Y3")):
        if yr <= horizon:
            fig.add_vline(x=yr, line=dict(color=_GRAY, dash="dot", width=1), row=1, col=1)
            fig.add_annotation(
                x=yr,
                y=max(cum) * 0.96,
                text=label,
                showarrow=False,
                font=dict(color=_GRAY, size=10),
                row=1,
                col=1,
            )

    bar_vals = [year1, year3]
    bar_colors = [_GREEN if v >= 0 else _RED for v in bar_vals]

    fig.add_trace(
        go.Bar(
            x=["Year 1", "Year 3"],
            y=bar_vals,
            marker_color=bar_colors,
            text=[f"€{v:,.0f}" for v in bar_vals],
            textposition="outside",
            name="Net Benefit",
            showlegend=False,
            width=0.4,
        ),
        row=1,
        col=2,
    )

    fig.add_hline(y=0, line=dict(color=_GRAY, dash="dot", width=1), row=1, col=2)

    fig.update_layout(
        height=420,
        width=900,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=12, color="#212121"),
        margin=dict(l=65, r=45, t=55, b=55),
        legend=dict(orientation="h", x=0.0, y=-0.15, font_size=11),
    )
    fig.update_xaxes(title_text="Month", row=1, col=1, gridcolor="#F0F0F0", zeroline=False)
    fig.update_yaxes(
        title_text="Cumulative Value (€)",
        row=1,
        col=1,
        gridcolor="#F0F0F0",
        tickformat=",.0f",
    )
    fig.update_xaxes(row=1, col=2, gridcolor="#F0F0F0")
    fig.update_yaxes(
        title_text="Net Benefit (€)",
        row=1,
        col=2,
        gridcolor="#F0F0F0",
        tickformat=",.0f",
    )

    return fig


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate ROI payback chart PNG from an arch-review markdown file.")
    p.add_argument("source", type=Path, help="Arch-review .md file with #region roi_summary")
    p.add_argument(
        "--out",
        "-o",
        type=Path,
        default=None,
        help="Output PNG (default: <source-dir>/roi-chart.png)",
    )
    p.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="Kaleido scale factor for resolution (default: 2.0)",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    if not args.source.exists():
        sys.exit(f"ERROR: file not found: {args.source}")

    roi = _extract_roi(args.source)
    fig = _build_figure(roi)

    out: Path = args.out or (args.source.parent / "roi-chart.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    fig.write_image(str(out), scale=args.scale)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
