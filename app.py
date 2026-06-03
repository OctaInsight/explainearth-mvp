import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ExplainEarth — Environmental Decision Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── COLOUR PALETTE (matches pitch deck) ──────────────────────────────────────
BG       = "#0a1a14"
TEAL     = "#1D9E75"
TEAL2    = "#0F6E56"
LIGHT    = "#c5e8d8"
DIM      = "#7ec8a4"
CARD     = "#0f2a1e"
CARD2    = "#112e1f"
WHITE    = "#f0faf6"
RED      = "#e07a5f"
AMBER    = "#e09a3f"

# ── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* App background */
  .stApp {{ background-color: {BG}; }}
  [data-testid="stSidebar"] {{ background-color: {CARD}; border-right: 1px solid {TEAL2}; }}
  [data-testid="stSidebar"] * {{ color: {LIGHT} !important; }}

  /* Hide Streamlit chrome */
  #MainMenu, footer, header {{ visibility: hidden; }}

  /* Metric cards */
  [data-testid="metric-container"] {{
    background: {CARD};
    border: 0.5px solid {TEAL2};
    border-radius: 8px;
    padding: 12px 16px;
  }}
  [data-testid="metric-container"] label {{ color: {DIM} !important; font-size: 12px !important; }}
  [data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {TEAL} !important; font-size: 26px !important; font-weight: 700 !important;
  }}
  [data-testid="metric-container"] [data-testid="stMetricDelta"] {{ font-size: 12px !important; }}

  /* Text colours */
  h1, h2, h3, h4 {{ color: {WHITE} !important; }}
  p, li, label, .stMarkdown {{ color: {LIGHT} !important; }}
  .stSelectbox label, .stSlider label {{ color: {DIM} !important; }}

  /* Alert / info boxes */
  .alert-red {{
    background: #2a0f0a; border-left: 4px solid {RED};
    border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;
  }}
  .alert-amber {{
    background: #2a1f0a; border-left: 4px solid {AMBER};
    border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;
  }}
  .alert-green {{
    background: #0a2a1a; border-left: 4px solid {TEAL};
    border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;
  }}
  .rec-card {{
    background: {CARD2}; border: 0.5px solid {TEAL2};
    border-left: 4px solid {TEAL}; border-radius: 6px;
    padding: 14px 18px; margin-bottom: 10px;
  }}
  .rec-title {{ color: {TEAL}; font-weight: 600; font-size: 14px; margin: 0 0 4px; }}
  .rec-body  {{ color: {LIGHT}; font-size: 13px; margin: 0; }}
  .section-header {{
    color: {TEAL}; font-size: 11px; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    border-bottom: 1px solid {TEAL2}; padding-bottom: 4px; margin-bottom: 12px;
  }}
  .brand {{ font-size: 20px; font-weight: 700; color: {WHITE}; }}
  .brand-sub {{ font-size: 11px; color: {DIM}; letter-spacing: 0.06em; }}
  .status-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: {TEAL}; display: inline-block; margin-right: 6px;
    animation: pulse 2s infinite;
  }}
  @keyframes pulse {{
    0%,100% {{ opacity:1; }} 50% {{ opacity:0.4; }}
  }}
  div[data-testid="stHorizontalBlock"] > div {{
    background: transparent !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── SITE DATA ─────────────────────────────────────────────────────────────────
SITES = {
    "Site 4 — Hardangerfjord": {
        "lat": 60.15, "lon": 6.35,
        "sst": 13.8, "sst_trend": "+1.4°C vs baseline",
        "nutrient": 0.68, "chlorophyll": 4.2,
        "wind": "SW 6 m/s", "current": "0.18 m/s anomaly",
        "risk": 75, "risk_level": "HIGH",
        "weeks": [20, 30, 45, 60, 75],
        "fish_tonnes": 420,
    },
    "Site 7 — Sognefjord": {
        "lat": 61.05, "lon": 6.10,
        "sst": 11.2, "sst_trend": "+0.6°C vs baseline",
        "nutrient": 0.38, "chlorophyll": 1.8,
        "wind": "NW 4 m/s", "current": "0.04 m/s anomaly",
        "risk": 28, "risk_level": "LOW",
        "weeks": [12, 18, 22, 25, 28],
        "fish_tonnes": 310,
    },
    "Site 12 — Nordfjord": {
        "lat": 61.85, "lon": 5.55,
        "sst": 12.4, "sst_trend": "+0.9°C vs baseline",
        "nutrient": 0.52, "chlorophyll": 2.9,
        "wind": "W 5 m/s", "current": "0.09 m/s anomaly",
        "risk": 52, "risk_level": "MEDIUM",
        "weeks": [18, 26, 36, 44, 52],
        "fish_tonnes": 280,
    },
    "Site 2 — Boknafjord": {
        "lat": 59.15, "lon": 5.65,
        "sst": 14.2, "sst_trend": "+1.8°C vs baseline",
        "nutrient": 0.71, "chlorophyll": 5.1,
        "wind": "S 7 m/s", "current": "0.22 m/s anomaly",
        "risk": 82, "risk_level": "CRITICAL",
        "weeks": [28, 42, 58, 72, 82],
        "fish_tonnes": 510,
    },
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 8px 0 20px;">
      <div class="brand">🌍 ExplainEarth</div>
      <div class="brand-sub">ENVIRONMENTAL DECISION INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("", ["Overview", "HAB Risk Monitor", "Forecast", "Recommendations", "About"], label_visibility="collapsed")

    st.markdown('<div class="section-header" style="margin-top:24px;">Site Selection</div>', unsafe_allow_html=True)
    selected_site = st.selectbox("Active site", list(SITES.keys()), label_visibility="collapsed")
    site = SITES[selected_site]

    st.markdown('<div class="section-header" style="margin-top:24px;">System Status</div>', unsafe_allow_html=True)
    st.markdown(f'<span class="status-dot"></span><span style="color:{TEAL};font-size:13px;">All systems operational</span>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:11px;color:{DIM};margin-top:8px;">Last update: {datetime.now().strftime("%Y-%m-%d %H:%M")} UTC</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:11px;color:{DIM};">Data: Copernicus · CMEMS · MET Norway · NOAA</p>', unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def risk_colour(level):
    return {"CRITICAL": RED, "HIGH": AMBER, "MEDIUM": "#d4c44a", "LOW": TEAL}[level]

def risk_badge(level, pct):
    col = risk_colour(level)
    return f'<span style="background:{col}22;border:1px solid {col};color:{col};border-radius:4px;padding:3px 10px;font-size:12px;font-weight:600;">{level} — {pct}%</span>'

def forecast_chart(site):
    weeks = ["Now", "Week 1", "Week 2", "Week 3", "Week 4"]
    probs = site["weeks"]
    threshold = 60

    fig = go.Figure()
    # Shaded danger zone
    fig.add_hrect(y0=threshold, y1=100, fillcolor=RED, opacity=0.08, line_width=0)
    # Threshold line
    fig.add_hline(y=threshold, line_dash="dash", line_color=RED, line_width=1,
                  annotation_text="Action threshold (60%)", annotation_font_color=RED,
                  annotation_font_size=11)
    # Probability line
    fig.add_trace(go.Scatter(
        x=weeks, y=probs,
        mode="lines+markers+text",
        line=dict(color=TEAL, width=3),
        marker=dict(size=9, color=TEAL, line=dict(color=WHITE, width=1.5)),
        text=[f"{p}%" for p in probs],
        textposition="top center",
        textfont=dict(color=WHITE, size=12),
        fill="tozeroy",
        fillcolor="rgba(29,158,117,0.09)",
        name="HAB probability",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CARD,
        font=dict(color=LIGHT, family="Arial"),
        xaxis=dict(showgrid=False, color=DIM, linecolor=TEAL2),
        yaxis=dict(showgrid=True, gridcolor="rgba(15,110,86,0.27)", color=DIM,
                   range=[0, 105], ticksuffix="%", linecolor=TEAL2),
        margin=dict(l=40, r=20, t=20, b=40),
        height=280,
        showlegend=False,
    )
    return fig

def map_chart(selected):
    fig = go.Figure()

    # ── Simplified Norwegian coastline outline (approximate polygon points) ──
    # Western Norway coast: Boknafjord up to Nordfjord latitude
    coast_lon = [4.5, 5.0, 5.2, 5.5, 5.3, 5.8, 6.0, 5.9, 6.2, 6.5,
                 6.3, 6.8, 7.0, 6.9, 7.2, 7.5, 7.8, 8.0, 8.3, 8.5,
                 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.5]
    coast_lat = [59.0, 59.1, 59.4, 59.5, 59.8, 60.0, 60.1, 60.4, 60.6, 60.8,
                 61.0, 61.2, 61.4, 61.6, 61.8, 62.0, 62.3, 62.6, 62.8, 63.0,
                 63.2, 63.2, 63.2, 63.2, 63.2, 63.2, 63.2, 63.2, 63.2, 59.0]

    fig.add_trace(go.Scatter(
        x=coast_lon, y=coast_lat,
        mode="lines",
        line=dict(color=TEAL2, width=1.5),
        fill="toself",
        fillcolor="rgba(15,110,86,0.08)",
        hoverinfo="skip",
        showlegend=False,
        name="coastline",
    ))

    # Fjord labels
    fjords = [
        (6.35, 60.2, "Hardangerfjord"),
        (6.1,  61.0, "Sognefjord"),
        (5.55, 61.85,"Nordfjord"),
        (5.65, 59.15,"Boknafjord"),
    ]
    for flon, flat, fname in fjords:
        fig.add_annotation(
            x=flon, y=flat + 0.25,
            text=fname,
            font=dict(color=DIM, size=9, family="Arial"),
            showarrow=False,
        )

    # ── Site markers ──
    for name, s in SITES.items():
        short = name.split("—")[1].strip()
        col = risk_colour(s["risk_level"])
        is_sel = name == selected
        sz = 14 + s["risk"] // 9

        # Pulse ring for selected site
        if is_sel:
            fig.add_trace(go.Scatter(
                x=[s["lon"]], y=[s["lat"]],
                mode="markers",
                marker=dict(size=sz+12, color="rgba(0,0,0,0)",
                            line=dict(color=col, width=2)),
                hoverinfo="skip", showlegend=False,
            ))

        fig.add_trace(go.Scatter(
            x=[s["lon"]], y=[s["lat"]],
            mode="markers+text",
            marker=dict(
                size=sz,
                color=col,
                opacity=1.0 if is_sel else 0.8,
                line=dict(color=WHITE, width=2 if is_sel else 1),
            ),
            text=[f"  {short}  {s['risk']}%"],
            textposition="middle right",
            textfont=dict(color=WHITE, size=11, family="Arial"),
            hovertemplate=(
                f"<b>{short}</b><br>"
                f"HAB Risk: {s['risk']}%<br>"
                f"Risk: {s['risk_level']}<br>"
                f"SST: {s['sst']}°C<extra></extra>"
            ),
            showlegend=False,
        ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CARD,
        margin=dict(l=50, r=20, t=10, b=50),
        height=380,
        showlegend=False,
        xaxis=dict(
            title=dict(text="Longitude (°E)", font=dict(color=DIM, size=11)),
            range=[4.2, 9.5],
            color=DIM, linecolor=TEAL2,
            gridcolor="rgba(15,110,86,0.15)",
            tickfont=dict(color=DIM, size=10),
            dtick=1,
        ),
        yaxis=dict(
            title=dict(text="Latitude (°N)", font=dict(color=DIM, size=11)),
            range=[58.5, 63.5],
            color=DIM, linecolor=TEAL2,
            gridcolor="rgba(15,110,86,0.15)",
            tickfont=dict(color=DIM, size=10),
            dtick=1,
        ),
        annotations=[
            dict(x=0.01, y=0.99, xref="paper", yref="paper",
                 text="Norwegian Aquaculture Sites — HAB Risk Monitor",
                 showarrow=False, font=dict(color=LIGHT, size=11),
                 xanchor="left", yanchor="top"),
        ],
    )
    return fig

def sst_map():
    # Simulated SST grid over Norwegian coast — pure Plotly heatmap, no token needed
    lats = np.linspace(58.5, 63.0, 40)
    lons = np.linspace(4.5, 8.5, 40)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Simulate SST with warm anomalies near high-risk sites
    sst = 11.0 \
        + 2.5 * np.exp(-((lat_grid-60.2)**2 + (lon_grid-6.4)**2) / 1.2) \
        + 1.8 * np.exp(-((lat_grid-59.2)**2 + (lon_grid-5.7)**2) / 0.8) \
        + 0.8 * np.exp(-((lat_grid-61.9)**2 + (lon_grid-5.6)**2) / 0.6) \
        + np.random.RandomState(42).normal(0, 0.12, lon_grid.shape)

    # Round lat/lon labels nicely
    lat_labels = [f"{l:.1f}°N" for l in lats[::4]]
    lon_labels = [f"{l:.1f}°E" for l in lons[::4]]

    fig = go.Figure()

    # Main heatmap
    fig.add_trace(go.Heatmap(
        z=sst,
        x=lons.tolist(),
        y=lats.tolist(),
        colorscale=[
            [0.0,  "#0a2a4a"],
            [0.25, "#0a3a2a"],
            [0.5,  "#0F6E56"],
            [0.75, "#e09a3f"],
            [1.0,  "#e07a5f"],
        ],
        zmin=9.5, zmax=14.5,
        colorbar=dict(
            title=dict(text="SST °C", font=dict(color=LIGHT, size=12)),
            tickfont=dict(color=LIGHT, size=11),
            tickvals=[10, 11, 12, 13, 14],
            ticktext=["10°C", "11°C", "12°C", "13°C", "14°C"],
            thickness=14,
            len=0.8,
        ),
        hovertemplate="Lon: %{x:.2f}°E<br>Lat: %{y:.2f}°N<br>SST: %{z:.1f}°C<extra></extra>",
        name="SST",
    ))

    # Overlay aquaculture site markers as scatter points
    site_lons = [s["lon"] for s in SITES.values()]
    site_lats = [s["lat"] for s in SITES.values()]
    site_names = [n.split("—")[1].strip() for n in SITES.keys()]
    site_risks = [s["risk"] for s in SITES.values()]
    site_ssts  = [s["sst"] for s in SITES.values()]
    site_cols  = [risk_colour(s["risk_level"]) for s in SITES.values()]

    for i in range(len(site_lons)):
        fig.add_trace(go.Scatter(
            x=[site_lons[i]], y=[site_lats[i]],
            mode="markers+text",
            marker=dict(
                size=16,
                color=site_cols[i],
                line=dict(color=WHITE, width=2),
                symbol="circle",
            ),
            text=[site_names[i]],
            textposition="top right",
            textfont=dict(color=WHITE, size=11, family="Arial"),
            hovertemplate=(
                f"<b>{site_names[i]}</b><br>"
                f"HAB Risk: {site_risks[i]}%<br>"
                f"SST: {site_ssts[i]}°C<extra></extra>"
            ),
            showlegend=False,
        ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CARD,
        margin=dict(l=50, r=20, t=10, b=50),
        height=380,
        xaxis=dict(
            title=dict(text="Longitude (°E)", font=dict(color=DIM, size=11)),
            range=[4.2, 9.0],
            color=DIM, gridcolor="rgba(15,110,86,0.15)", linecolor=TEAL2,
            tickfont=dict(color=DIM, size=10), dtick=1,
        ),
        yaxis=dict(
            title=dict(text="Latitude (°N)", font=dict(color=DIM, size=11)),
            range=[58.2, 63.3],
            color=DIM, gridcolor="rgba(15,110,86,0.15)", linecolor=TEAL2,
            tickfont=dict(color=DIM, size=10), dtick=1,
        ),
        annotations=[dict(
            x=0.01, y=0.98, xref="paper", yref="paper",
            text="Norwegian Coast — Sea Surface Temperature (°C)",
            showarrow=False,
            font=dict(color=LIGHT, size=11),
            bgcolor=CARD, bordercolor=TEAL2, borderwidth=1,
            xanchor="left", yanchor="top",
        )],
    )
    return fig

# ── PAGE: OVERVIEW ────────────────────────────────────────────────────────────
if page == "Overview":
    st.markdown(f'<h1 style="font-size:26px;margin-bottom:4px;">Norwegian Coastline — Risk Overview</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{DIM};font-size:13px;margin-bottom:20px;">Real-time environmental decision intelligence · {datetime.now().strftime("%d %B %Y, %H:%M")} UTC</p>', unsafe_allow_html=True)

    # Alert banner for critical/high sites
    critical = [n for n, s in SITES.items() if s["risk_level"] in ("CRITICAL","HIGH")]
    if critical:
        for c in critical:
            s = SITES[c]
            col = risk_colour(s["risk_level"])
            label = c.split("—")[1].strip()
            st.markdown(f"""
            <div class="alert-{'red' if s['risk_level']=='CRITICAL' else 'amber'}">
              <strong style="color:{col};">⚠ {s['risk_level']} ALERT — {label}</strong>
              <span style="color:{LIGHT};font-size:13px;margin-left:12px;">HAB probability {s['risk']}% · Action required within 4 weeks</span>
            </div>""", unsafe_allow_html=True)

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Active sites monitored", "4", "Norwegian coast")
    with c2: st.metric("Critical alerts", "1", "Site 2 — Boknafjord")
    with c3: st.metric("High risk sites", "2", "Require attention")
    with c4: st.metric("Total biomass at risk", "930 t", "€2.8M exposure")

    st.markdown("<br>", unsafe_allow_html=True)
    col_map, col_list = st.columns([1.6, 1])

    with col_map:
        st.markdown('<div class="section-header">Site Risk Map</div>', unsafe_allow_html=True)
        st.plotly_chart(map_chart(selected_site), use_container_width=True, config={"displayModeBar": False})

    with col_list:
        st.markdown('<div class="section-header">All Sites — Risk Summary</div>', unsafe_allow_html=True)
        for name, s in SITES.items():
            short = name.split("—")[1].strip()
            col = risk_colour(s["risk_level"])
            st.markdown(f"""
            <div style="background:{CARD};border:.5px solid {TEAL2};border-left:4px solid {col};
                        border-radius:6px;padding:10px 14px;margin-bottom:8px;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="color:{WHITE};font-weight:600;font-size:13px;">{short}</span>
                <span style="color:{col};font-size:13px;font-weight:700;">{s['risk']}%</span>
              </div>
              <div style="color:{DIM};font-size:11px;margin-top:2px;">SST {s['sst']}°C · {s['sst_trend']}</div>
            </div>""", unsafe_allow_html=True)

# ── PAGE: HAB RISK MONITOR ────────────────────────────────────────────────────
elif page == "HAB Risk Monitor":
    short = selected_site.split("—")[1].strip()
    st.markdown(f'<h1 style="font-size:26px;margin-bottom:4px;">HAB Risk Monitor — {short}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{DIM};font-size:13px;margin-bottom:20px;">Harmful algal bloom probability · ExplainEarth AI model · Updated {datetime.now().strftime("%H:%M")} UTC</p>', unsafe_allow_html=True)

    # Main alert
    col = risk_colour(site["risk_level"])
    cls = {"CRITICAL":"red","HIGH":"amber","MEDIUM":"amber","LOW":"green"}[site["risk_level"]]
    st.markdown(f"""
    <div class="alert-{cls}" style="display:flex;align-items:center;gap:24px;padding:18px 24px;">
      <div style="font-size:48px;font-weight:800;color:{col};">{site['risk']}%</div>
      <div>
        <div style="color:{col};font-size:18px;font-weight:700;">HAB Alert — {short}</div>
        <div style="color:{LIGHT};font-size:13px;margin-top:4px;">Harmful algal bloom probability · {site['risk_level']} risk · Action required within 4 weeks</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Environmental signals
    st.markdown('<div class="section-header" style="margin-top:20px;">Environmental Signals</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Sea surface temp", f"{site['sst']}°C", site["sst_trend"])
    with c2: st.metric("Nutrient load index", f"{site['nutrient']}", "above threshold" if site["nutrient"]>0.5 else "normal")
    with c3: st.metric("Chlorophyll-a", f"{site['chlorophyll']} μg/L", "elevated" if site["chlorophyll"]>3 else "normal")
    with c4: st.metric("Current anomaly", site["current"], "HAB transport risk" if site["risk"]>50 else "low")

    # Signal flow
    st.markdown('<div class="section-header" style="margin-top:20px;">Signal Detection Chain</div>', unsafe_allow_html=True)
    signals = [
        ("🌡", "SST rising", site["sst_trend"]),
        ("🧪", "Nutrient load shift", f"Index {site['nutrient']}"),
        ("💨", "Wind pattern", site["wind"]),
        ("🌊", "Current anomaly", site["current"]),
    ]
    cols = st.columns(4)
    for col_obj, (icon, label, val) in zip(cols, signals):
        with col_obj:
            st.markdown(f"""
            <div style="background:{CARD};border:.5px solid {TEAL2};border-radius:6px;
                        padding:12px;text-align:center;">
              <div style="font-size:24px;">{icon}</div>
              <div style="color:{WHITE};font-size:12px;font-weight:600;margin-top:4px;">{label}</div>
              <div style="color:{DIM};font-size:11px;margin-top:2px;">{val}</div>
            </div>""", unsafe_allow_html=True)

    # SST map
    st.markdown('<div class="section-header" style="margin-top:20px;">Sea Surface Temperature — Norwegian Coast</div>', unsafe_allow_html=True)
    st.plotly_chart(sst_map(), use_container_width=True, config={"displayModeBar": False})

# ── PAGE: FORECAST ────────────────────────────────────────────────────────────
elif page == "Forecast":
    short = selected_site.split("—")[1].strip()
    st.markdown(f'<h1 style="font-size:26px;margin-bottom:4px;">4-Week HAB Forecast — {short}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{DIM};font-size:13px;margin-bottom:20px;">ExplainEarth predictive model · AccEARTH GeoAI framework · Confidence interval 85%</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="section-header">Probability Forecast</div>', unsafe_allow_html=True)
        st.plotly_chart(forecast_chart(site), use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown('<div class="section-header">Forecast Summary</div>', unsafe_allow_html=True)
        weeks = ["Now", "Week 1", "Week 2", "Week 3", "Week 4"]
        for w, p in zip(weeks, site["weeks"]):
            col = RED if p >= 60 else AMBER if p >= 40 else TEAL
            st.markdown(f"""
            <div style="background:{CARD};border:.5px solid {TEAL2};border-radius:5px;
                        padding:8px 12px;margin-bottom:6px;display:flex;
                        justify-content:space-between;align-items:center;">
              <span style="color:{LIGHT};font-size:13px;">{w}</span>
              <span style="color:{col};font-weight:700;font-size:14px;">{p}%</span>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:{CARD2};border:.5px solid {TEAL};border-radius:6px;
                    padding:12px;margin-top:12px;">
          <div style="color:{TEAL};font-size:11px;font-weight:600;letter-spacing:.05em;
                      text-transform:uppercase;">Financial exposure</div>
          <div style="color:{WHITE};font-size:20px;font-weight:700;margin-top:4px;">
            €{site['fish_tonnes'] * 4800 / 1000:.1f}M
          </div>
          <div style="color:{DIM};font-size:11px;margin-top:2px;">
            {site['fish_tonnes']}t biomass at risk · €4,800/t avg value
          </div>
        </div>""", unsafe_allow_html=True)

    # Model inputs
    st.markdown('<div class="section-header" style="margin-top:20px;">Model Input Variables</div>', unsafe_allow_html=True)
    model_data = pd.DataFrame({
        "Variable": ["Sea Surface Temperature", "Nutrient Load Index", "Chlorophyll-a", "Wind Speed", "Current Velocity", "Historical HAB frequency"],
        "Value": [f"{site['sst']}°C", str(site['nutrient']), f"{site['chlorophyll']} μg/L", site['wind'], site['current'], "4 events / 10 years"],
        "Status": ["⚠ Elevated" if site['sst']>12 else "✓ Normal",
                   "⚠ High" if site['nutrient']>0.5 else "✓ Normal",
                   "⚠ Elevated" if site['chlorophyll']>3 else "✓ Normal",
                   "⚠ Active" if site['risk']>50 else "✓ Calm",
                   "⚠ Anomaly" if site['risk']>50 else "✓ Normal",
                   "⚠ Moderate" if site['risk']>40 else "✓ Low"],
        "Weight": ["28%", "24%", "18%", "14%", "10%", "6%"]
    })
    st.dataframe(model_data, use_container_width=True, hide_index=True)

# ── PAGE: RECOMMENDATIONS ─────────────────────────────────────────────────────
elif page == "Recommendations":
    short = selected_site.split("—")[1].strip()
    st.markdown(f'<h1 style="font-size:26px;margin-bottom:4px;">Decision Recommendations — {short}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{DIM};font-size:13px;margin-bottom:20px;">ExplainEarth Decision Intelligence · Based on {site["risk"]}% HAB probability forecast</p>', unsafe_allow_html=True)

    # ROI summary
    savings = site["fish_tonnes"] * 4800 / 1000
    st.markdown(f"""
    <div style="background:{CARD2};border:.5px solid {TEAL};border-radius:8px;
                padding:18px 24px;margin-bottom:24px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="color:{TEAL};font-size:11px;font-weight:600;letter-spacing:.06em;
                      text-transform:uppercase;">Estimated financial exposure</div>
          <div style="color:{WHITE};font-size:28px;font-weight:700;margin-top:4px;">
            €{savings:.1f}M
          </div>
          <div style="color:{DIM};font-size:12px;margin-top:2px;">
            {site['fish_tonnes']}t biomass · {site['risk']}% HAB probability · 4-week window
          </div>
        </div>
        <div style="text-align:right;">
          <div style="color:{TEAL};font-size:11px;font-weight:600;letter-spacing:.06em;
                      text-transform:uppercase;">ExplainEarth subscription</div>
          <div style="color:{WHITE};font-size:22px;font-weight:700;margin-top:4px;">€50–200K/yr</div>
          <div style="color:{DIM};font-size:12px;margin-top:2px;">Payback: first alert</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Recommendations
    recs_high = [
        ("🚢", "Move cages to lower-risk zone", "Relocate biomass to Site 7 — Sognefjord (28% HAB risk). Estimated cost: €80–120K. Estimated loss avoided: €1.8–3.2M."),
        ("📉", "Reduce stocking density immediately", "Lower biomass per cage by 30% to reduce environmental stress and mortality risk. Begin within 72 hours."),
        ("⏩", "Accelerate harvest schedule", f"Bring forward harvest of mature stock (est. {int(site['fish_tonnes']*0.4)}t). Reduces financial exposure by approximately €{site['fish_tonnes']*0.4*4800/1000:.1f}M."),
    ]
    recs_monitor = [
        ("📡", "Increase monitoring frequency", "Deploy additional IoT sensors at cage perimeter. Increase Copernicus SST data pull to 6-hour intervals."),
        ("📋", "Notify regulatory authority", "Submit early-warning report to Fiskeridirektoratet within 48 hours per Norwegian aquaculture regulations."),
    ]

    st.markdown('<div class="section-header">Priority Actions — Implement within 72 hours</div>', unsafe_allow_html=True)
    for icon, title, body in recs_high:
        st.markdown(f"""
        <div class="rec-card">
          <div class="rec-title">{icon} {title}</div>
          <div class="rec-body">{body}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:20px;">Monitoring Actions — Ongoing</div>', unsafe_allow_html=True)
    for icon, title, body in recs_monitor:
        st.markdown(f"""
        <div class="rec-card" style="border-left-color:{DIM};">
          <div class="rec-title" style="color:{DIM};">{icon} {title}</div>
          <div class="rec-body">{body}</div>
        </div>""", unsafe_allow_html=True)

    # SDG alignment
    st.markdown('<div class="section-header" style="margin-top:20px;">Mission Alignment</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{CARD};border:.5px solid {TEAL2};border-radius:8px;padding:16px 20px;">
      <p style="color:{LIGHT};font-size:13px;margin:0 0 8px;">
        When ExplainEarth prevents this HAB event, it is not just <strong style="color:{WHITE};">€{savings:.1f}M</strong> recovered.
        It is <strong style="color:{TEAL};">{site['fish_tonnes']}t of food</strong>, ocean biomass, and years of natural growth
        returned to people and planet — aligned with UN SDGs 2, 12, 13, and 14.
      </p>
      <p style="color:{DIM};font-size:12px;margin:0;">
        SDG 2 Zero Hunger · SDG 12 Responsible Consumption · SDG 13 Climate Action · SDG 14 Life Below Water
      </p>
    </div>""", unsafe_allow_html=True)

# ── PAGE: ABOUT ───────────────────────────────────────────────────────────────
elif page == "About":
    st.markdown(f'<h1 style="font-size:26px;margin-bottom:4px;">About ExplainEarth</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown(f"""
        <div style="background:{CARD};border:.5px solid {TEAL2};border-radius:8px;padding:20px 24px;margin-bottom:16px;">
          <div style="color:{TEAL};font-size:13px;font-weight:600;letter-spacing:.06em;
                      text-transform:uppercase;margin-bottom:10px;">Our Mission</div>
          <p style="color:{LIGHT};font-size:14px;line-height:1.7;margin:0;">
            ExplainEarth is an AI-powered Environmental Decision Intelligence Platform with a
            <strong style="color:{WHITE};">dual mission</strong>: to protect the financial value
            of industries — and to preserve the physical resources behind that value.
          </p>
          <p style="color:{LIGHT};font-size:14px;line-height:1.7;margin:12px 0 0;">
            When a €200M aquaculture loss is avoided, it is not just money recovered.
            It is food, ocean biomass, and years of natural growth returned to people and planet.
          </p>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:{CARD};border:.5px solid {TEAL2};border-radius:8px;padding:20px 24px;">
          <div style="color:{TEAL};font-size:13px;font-weight:600;letter-spacing:.06em;
                      text-transform:uppercase;margin-bottom:12px;">Four Intelligence Layers</div>
          {''.join([f"""
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
            <div style="background:{TEAL};color:{BG};font-weight:700;font-size:12px;
                        border-radius:4px;width:22px;height:22px;display:flex;
                        align-items:center;justify-content:center;flex-shrink:0;">{n}</div>
            <div>
              <div style="color:{WHITE};font-size:13px;font-weight:600;">{t}</div>
              <div style="color:{DIM};font-size:11px;">{s}</div>
            </div>
          </div>""" for n,t,s in [
            ("4","Decision Intelligence","What to do — actionable recommendations"),
            ("3","Future Intelligence","What will happen — 4-week forecast"),
            ("2","GeoAI","Why it is happening — environmental risk models"),
            ("1","Earth Intelligence","What is happening — real-time Earth data"),
          ]])}
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background:{CARD};border:.5px solid {TEAL2};border-radius:8px;padding:20px 24px;margin-bottom:16px;">
          <div style="color:{TEAL};font-size:13px;font-weight:600;letter-spacing:.06em;
                      text-transform:uppercase;margin-bottom:12px;">Data Stack</div>
          {''.join([f'<div style="background:{CARD2};border-radius:4px;padding:7px 12px;margin-bottom:6px;color:{LIGHT};font-size:13px;">{d}</div>' for d in [
            "🛰 Copernicus Marine Service (CMEMS)",
            "🛰 ESA Sentinel Earth Observation",
            "🌊 NOAA Ocean Data",
            "🌤 MET Norway Weather API",
            "📡 IoT Sensor Networks",
          ]])}
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:{CARD};border:.5px solid {TEAL2};border-radius:8px;padding:20px 24px;">
          <div style="color:{TEAL};font-size:13px;font-weight:600;letter-spacing:.06em;
                      text-transform:uppercase;margin-bottom:12px;">Founder</div>
          <div style="color:{WHITE};font-size:15px;font-weight:600;">Dr. Tamer Abu-Alam</div>
          <div style="color:{TEAL};font-size:12px;margin-bottom:10px;">Founder & CEO, ExplainEarth (in formation)</div>
          <div style="color:{DIM};font-size:12px;line-height:1.6;">
            25+ years Earth science · AI & sustainability analytics ·
            €28M+ innovation portfolio · 65+ peer-reviewed papers ·
            CloudEARTHi founder — 50+ organisations across 13 countries
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{CARD2};border:.5px solid {TEAL};border-radius:8px;
                padding:14px 20px;margin-top:16px;text-align:center;">
      <span style="color:{TEAL};font-style:italic;font-size:14px;font-weight:500;">
        "The Earth is already sending the signals. ExplainEarth makes them actionable."
      </span>
    </div>""", unsafe_allow_html=True)
