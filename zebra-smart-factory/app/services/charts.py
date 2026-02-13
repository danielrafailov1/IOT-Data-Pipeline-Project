"""Plotly chart generation for SPC, heatmaps, Pareto."""
from typing import Any
import plotly.graph_objects as go
import pandas as pd
from app.services.spc import ControlLimits, simple_limits, cusum, xbar_r_limits


def spc_xbar_chart(
    values: list[float],
    labels: list[str] | None = None,
    subgroup_size: int = 5,
) -> dict[str, Any]:
    """Generate X-bar control chart as Plotly JSON."""
    if labels is None:
        labels = [str(i) for i in range(len(values))]
    xbar_lim, _ = xbar_r_limits(values, subgroup_size)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=values,
            mode="lines+markers",
            name="Values",
            line=dict(color="#2563eb"),
        )
    )
    fig.add_hline(y=xbar_lim.center, line_dash="dash", line_color="green", annotation_text="CL")
    fig.add_hline(y=xbar_lim.ucl, line_dash="dot", line_color="red", annotation_text="UCL")
    fig.add_hline(y=xbar_lim.lcl, line_dash="dot", line_color="red", annotation_text="LCL")
    fig.update_layout(
        title="X-bar Control Chart",
        xaxis_title="Sample",
        yaxis_title="Value",
        template="plotly_white",
    )
    return fig.to_json()


def spc_cusum_chart(values: list[float], labels: list[str] | None = None) -> dict[str, Any]:
    """Generate CUSUM chart as Plotly JSON."""
    if labels is None:
        labels = [str(i) for i in range(len(values))]
    cusum_vals = cusum(values)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=cusum_vals,
            mode="lines+markers",
            name="CUSUM",
            line=dict(color="#7c3aed"),
        )
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        title="CUSUM Chart",
        xaxis_title="Sample",
        yaxis_title="CUSUM",
        template="plotly_white",
    )
    return fig.to_json()


def heatmap_chart(df: pd.DataFrame, x: str, y: str, z: str) -> dict[str, Any]:
    """Generate heatmap from DataFrame."""
    pivot = df.pivot_table(index=y, columns=x, values=z, aggfunc="mean")
    fig = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index, colorscale="Viridis"))
    fig.update_layout(
        title=f"Heatmap: {z} by {x} x {y}",
        xaxis_title=x,
        yaxis_title=y,
        template="plotly_white",
    )
    return fig.to_json()


def pareto_chart(labels: list[str], values: list[float], title: str = "Pareto Chart") -> dict[str, Any]:
    """Generate Pareto chart (sorted bar + cumulative %)."""
    pairs = sorted(zip(labels, values), key=lambda x: -x[1])
    labels_sorted = [p[0] for p in pairs]
    values_sorted = [p[1] for p in pairs]
    total = sum(values_sorted)
    cumsum = [sum(values_sorted[: i + 1]) / total * 100 if total > 0 else 0 for i in range(len(values_sorted))]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=labels_sorted, y=values_sorted, name="Count", marker_color="#2563eb")
    )
    fig.add_trace(
        go.Scatter(
            x=labels_sorted,
            y=cumsum,
            mode="lines+markers",
            name="Cumulative %",
            yaxis="y2",
            line=dict(color="#dc2626"),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Category",
        yaxis_title="Count",
        yaxis2=dict(overlaying="y", side="right", range=[0, 105], title="Cumulative %"),
        template="plotly_white",
        showlegend=True,
    )
    return fig.to_json()
