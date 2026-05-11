"""Visual theme. Restrained on purpose."""

# One accent color, not two. Slate teal.
ACCENT = "#0F766E"
ACCENT_SOFT = "#5EEAD4"
WARN = "#B45309"
NEUTRAL = "#475569"
NEUTRAL_LIGHT = "#94A3B8"
SURFACE = "#F8FAFC"
TEXT = "#0F172A"

# Five-band signal scale
BAND_COLORS = {
    "silent":      "#CBD5E1",
    "occasional":  "#94A3B8",
    "supportive":  "#64748B",
    "reinforcing": "#0F766E",
    "modeling":    "#0E7490",
}

# Diagnosis state colors
STATE_COLORS = {
    "healthy":   "#0F766E",
    "watch":     "#B45309",
    "intervene": "#9F1239",
    "unknown":   "#94A3B8",
}


def plotly_theme(fig, height=380):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=40, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
                  size=12, color=TEXT),
        xaxis=dict(showgrid=True, gridcolor="#E2E8F0", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig
