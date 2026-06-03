import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(
    page_title="ExplainEarth — Environmental Decision Intelligence",
    page_icon="🌍", layout="wide", initial_sidebar_state="expanded",
)

BG    = "#0a1a14"; TEAL  = "#1D9E75"; TEAL2 = "#0F6E56"
LIGHT = "#c5e8d8"; DIM   = "#7ec8a4"; CARD  = "#0f2a1e"
CARD2 = "#112e1f"; WHITE = "#f0faf6"; RED   = "#e07a5f"; AMBER = "#e09a3f"

st.markdown(f"""<style>
  .stApp{{background-color:{BG};}}
  [data-testid="stSidebar"]{{background-color:{CARD};border-right:1px solid {TEAL2};}}
  [data-testid="stSidebar"] *{{color:{LIGHT}!important;}}
  #MainMenu,footer,header{{visibility:hidden;}}
  [data-testid="metric-container"]{{background:{CARD};border:0.5px solid {TEAL2};border-radius:8px;padding:12px 16px;}}
  [data-testid="metric-container"] label{{color:{DIM}!important;font-size:12px!important;}}
  [data-testid="metric-container"] [data-testid="stMetricValue"]{{color:{TEAL}!important;font-size:26px!important;font-weight:700!important;}}
  h1,h2,h3,h4{{color:{WHITE}!important;}}
  p,li,.stMarkdown{{color:{LIGHT}!important;}}
  .shdr{{color:{TEAL};font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;border-bottom:1px solid {TEAL2};padding-bottom:4px;margin-bottom:12px;}}
  .alert-red{{background:#2a0f0a;border-left:4px solid {RED};border-radius:6px;padding:14px 18px;margin-bottom:12px;}}
  .alert-amber{{background:#2a1f0a;border-left:4px solid {AMBER};border-radius:6px;padding:14px 18px;margin-bottom:12px;}}
  .alert-green{{background:#0a2a1a;border-left:4px solid {TEAL};border-radius:6px;padding:14px 18px;margin-bottom:12px;}}
  .rec{{background:{CARD2};border:0.5px solid {TEAL2};border-left:4px solid {TEAL};border-radius:6px;padding:14px 18px;margin-bottom:10px;}}
</style>""", unsafe_allow_html=True)

SITES = {
    "Site 4 — Hardangerfjord": {"lat":60.15,"lon":6.35,"sst":13.8,"sst_trend":"+1.4°C vs baseline","nutrient":0.68,"chlorophyll":4.2,"wind":"SW 6 m/s","current":"0.18 m/s anomaly","risk":75,"risk_level":"HIGH","weeks":[20,30,45,60,75],"fish_tonnes":420},
    "Site 7 — Sognefjord":     {"lat":61.05,"lon":6.10,"sst":11.2,"sst_trend":"+0.6°C vs baseline","nutrient":0.38,"chlorophyll":1.8,"wind":"NW 4 m/s","current":"0.04 m/s anomaly","risk":28,"risk_level":"LOW","weeks":[12,18,22,25,28],"fish_tonnes":310},
    "Site 12 — Nordfjord":     {"lat":61.85,"lon":5.55,"sst":12.4,"sst_trend":"+0.9°C vs baseline","nutrient":0.52,"chlorophyll":2.9,"wind":"W 5 m/s","current":"0.09 m/s anomaly","risk":52,"risk_level":"MEDIUM","weeks":[18,26,36,44,52],"fish_tonnes":280},
    "Site 2 — Boknafjord":     {"lat":59.15,"lon":5.65,"sst":14.2,"sst_trend":"+1.8°C vs baseline","nutrient":0.71,"chlorophyll":5.1,"wind":"S 7 m/s","current":"0.22 m/s anomaly","risk":82,"risk_level":"CRITICAL","weeks":[28,42,58,72,82],"fish_tonnes":510},
}

def rcol(lvl):  return {"CRITICAL":RED,"HIGH":AMBER,"MEDIUM":"#d4c44a","LOW":TEAL}[lvl]
def rfol(lvl):  return {"CRITICAL":"red","HIGH":"orange","MEDIUM":"beige","LOW":"green"}[lvl]

with st.sidebar:
    st.markdown(f'<div style="padding:8px 0 20px;"><div style="font-size:20px;font-weight:700;color:{WHITE};">🌍 ExplainEarth</div><div style="font-size:11px;color:{DIM};letter-spacing:.06em;">ENVIRONMENTAL DECISION INTELLIGENCE</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="shdr">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("", ["Overview","HAB Risk Monitor","Forecast","Recommendations","About"], label_visibility="collapsed")
    st.markdown(f'<div class="shdr" style="margin-top:20px;">Site Selection</div>', unsafe_allow_html=True)
    selected_site = st.selectbox("Site", list(SITES.keys()), label_visibility="collapsed")
    site = SITES[selected_site]
    st.markdown(f'<div class="shdr" style="margin-top:20px;">System Status</div>', unsafe_allow_html=True)
    st.markdown(f'<span style="color:{TEAL};font-size:13px;">● All systems operational</span>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:11px;color:{DIM};margin-top:6px;">Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")} UTC<br>Data: Copernicus · CMEMS · MET Norway</p>', unsafe_allow_html=True)

def forecast_chart(s):
    weeks=["Now","Week 1","Week 2","Week 3","Week 4"]; probs=s["weeks"]
    fig=go.Figure()
    fig.add_hrect(y0=60,y1=105,fillcolor="rgba(224,122,95,0.08)",line_width=0)
    fig.add_hline(y=60,line_dash="dash",line_color=RED,line_width=1.5,
                  annotation_text="Action threshold (60%)",annotation_font_color=RED,
                  annotation_font_size=11,annotation_position="top right")
    fig.add_trace(go.Scatter(x=weeks,y=probs,mode="lines+markers+text",
        line=dict(color=TEAL,width=3),marker=dict(size=10,color=TEAL,line=dict(color=WHITE,width=2)),
        text=[f"{p}%" for p in probs],textposition="top center",textfont=dict(color=WHITE,size=12),
        fill="tozeroy",fillcolor="rgba(29,158,117,0.10)"))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor=CARD,font=dict(color=LIGHT,family="Arial"),
        xaxis=dict(showgrid=False,color=DIM,linecolor=TEAL2),
        yaxis=dict(showgrid=True,gridcolor="rgba(15,110,86,0.25)",color=DIM,range=[0,110],ticksuffix="%",linecolor=TEAL2),
        margin=dict(l=40,r=20,t=20,b=40),height=300,showlegend=False)
    return fig

def overview_map():
    m = folium.Map(location=[60.5,6.0],zoom_start=7,tiles="CartoDB dark_matter",prefer_canvas=True)
    for name,s in SITES.items():
        short=name.split("—")[1].strip(); hc=rcol(s["risk_level"])
        popup_html=f"""<div style="font-family:Arial;min-width:170px;background:#0f2a1e;padding:10px;border-radius:6px;border:1px solid #0F6E56;">
          <b style="color:#f0faf6;">{short}</b><br>
          <span style="color:{hc};font-size:18px;font-weight:700;">{s['risk']}%</span>
          <span style="color:#7ec8a4;font-size:12px;"> HAB risk</span><br>
          <span style="color:#c5e8d8;font-size:12px;">Risk: {s['risk_level']}<br>SST: {s['sst']}°C ({s['sst_trend']})<br>Chlorophyll: {s['chlorophyll']} μg/L<br>Biomass: {s['fish_tonnes']}t</span></div>"""
        folium.CircleMarker(location=[s["lat"],s["lon"]],radius=10+s["risk"]//12,
            color=hc,fill=True,fill_color=hc,fill_opacity=0.85,weight=2,
            popup=folium.Popup(popup_html,max_width=220),
            tooltip=f"{short} — {s['risk_level']} ({s['risk']}%)").add_to(m)
        folium.Marker(location=[s["lat"]+0.07,s["lon"]+0.1],
            icon=folium.DivIcon(html=f'<div style="color:{hc};font-weight:700;font-size:12px;font-family:Arial;white-space:nowrap;text-shadow:1px 1px 2px #000;">{short}<br>{s["risk"]}%</div>',
            icon_size=(130,32),icon_anchor=(0,0))).add_to(m)
    return m

def sst_map(selected):
    m = folium.Map(location=[60.5,6.0],zoom_start=7,tiles="CartoDB dark_matter",prefer_canvas=True)
    rng=np.random.RandomState(42); heat=[]
    for la in np.linspace(58.4,63.2,70):
        for lo in np.linspace(4.7,8.6,70):
            val=(11.0
                +2.5*np.exp(-((la-60.15)**2+(lo-6.35)**2)/1.0)
                +2.0*np.exp(-((la-59.15)**2+(lo-5.65)**2)/0.7)
                +0.9*np.exp(-((la-61.85)**2+(lo-5.55)**2)/0.5)
                +rng.normal(0,0.08))
            w=max(0,min(1,(val-9.5)/5.5))
            if w>0.04: heat.append([la,lo,w])
    HeatMap(heat,min_opacity=0.35,max_opacity=0.85,radius=20,blur=22,
        gradient={"0.0":"#0a3a5a","0.3":"#0F6E56","0.65":"#e09a3f","1.0":"#e07a5f"}).add_to(m)
    for name,s in SITES.items():
        short=name.split("—")[1].strip(); hc=rcol(s["risk_level"]); sel=(name==selected)
        folium.CircleMarker(location=[s["lat"],s["lon"]],radius=11 if sel else 8,
            color=WHITE,fill=True,fill_color=hc,fill_opacity=1.0,weight=3 if sel else 1,
            tooltip=f"{short} — SST {s['sst']}°C · HAB {s['risk']}%").add_to(m)
        folium.Marker(location=[s["lat"]+0.07,s["lon"]+0.1],
            icon=folium.DivIcon(html=f'<div style="color:#f0faf6;font-size:11px;font-family:Arial;font-weight:700;white-space:nowrap;text-shadow:1px 1px 2px #000;">{short}<br><span style="color:{hc};">{s["sst"]}°C</span></div>',
            icon_size=(130,32),icon_anchor=(0,0))).add_to(m)
    return m

# ── OVERVIEW ──────────────────────────────────────────────────────────────────
if page=="Overview":
    st.markdown(f'<h1 style="font-size:26px;margin-bottom:4px;">Norwegian Coastline — Risk Overview</h1>',unsafe_allow_html=True)
    st.markdown(f'<p style="color:{DIM};font-size:13px;margin-bottom:16px;">Real-time environmental decision intelligence · {datetime.now().strftime("%d %B %Y, %H:%M")} UTC</p>',unsafe_allow_html=True)
    for name,s in SITES.items():
        if s["risk_level"] in ("CRITICAL","HIGH"):
            hc=rcol(s["risk_level"]); lb=name.split("—")[1].strip()
            cls="red" if s["risk_level"]=="CRITICAL" else "amber"
            st.markdown(f'<div class="alert-{cls}"><strong style="color:{hc};">⚠ {s["risk_level"]} — {lb}</strong><span style="color:{LIGHT};font-size:13px;margin-left:12px;">HAB probability {s["risk"]}% · Action required within 4 weeks</span></div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("Sites monitored","4","Norwegian coast")
    with c2: st.metric("Critical alerts","1","Boknafjord")
    with c3: st.metric("High risk sites","2","Require attention")
    with c4: st.metric("Biomass at risk","930 t","€2.8M exposure")
    st.markdown("<br>",unsafe_allow_html=True)
    cm,cl=st.columns([1.6,1])
    with cm:
        st.markdown(f'<div class="shdr">Site Risk Map — click a marker for details</div>',unsafe_allow_html=True)
        st_folium(overview_map(),width=None,height=420,returned_objects=[])
    with cl:
        st.markdown(f'<div class="shdr">All Sites — Risk Summary</div>',unsafe_allow_html=True)
        for name,s in SITES.items():
            short=name.split("—")[1].strip(); hc=rcol(s["risk_level"])
            st.markdown(f'<div style="background:{CARD};border:.5px solid {TEAL2};border-left:4px solid {hc};border-radius:6px;padding:10px 14px;margin-bottom:8px;"><div style="display:flex;justify-content:space-between;"><span style="color:{WHITE};font-weight:600;font-size:13px;">{short}</span><span style="color:{hc};font-size:14px;font-weight:700;">{s["risk"]}%</span></div><div style="color:{DIM};font-size:11px;margin-top:3px;">SST {s["sst"]}°C · {s["sst_trend"]} · {s["risk_level"]}</div></div>',unsafe_allow_html=True)

# ── HAB RISK MONITOR ──────────────────────────────────────────────────────────
elif page=="HAB Risk Monitor":
    short=selected_site.split("—")[1].strip()
    st.markdown(f'<h1 style="font-size:26px;margin-bottom:4px;">HAB Risk Monitor — {short}</h1>',unsafe_allow_html=True)
    st.markdown(f'<p style="color:{DIM};font-size:13px;margin-bottom:16px;">Harmful algal bloom probability · ExplainEarth AI model · {datetime.now().strftime("%H:%M")} UTC</p>',unsafe_allow_html=True)
    hc=rcol(site["risk_level"]); cls={"CRITICAL":"red","HIGH":"amber","MEDIUM":"amber","LOW":"green"}[site["risk_level"]]
    st.markdown(f'<div class="alert-{cls}" style="display:flex;align-items:center;gap:24px;padding:18px 24px;"><div style="font-size:52px;font-weight:800;color:{hc};line-height:1;">{site["risk"]}%</div><div><div style="color:{hc};font-size:18px;font-weight:700;">HAB Alert — {short}</div><div style="color:{LIGHT};font-size:13px;margin-top:4px;">Harmful algal bloom probability · {site["risk_level"]} · Action required within 4 weeks</div></div></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="shdr" style="margin-top:18px;">Environmental Signals</div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("Sea surface temp",f"{site['sst']}°C",site["sst_trend"])
    with c2: st.metric("Nutrient load",f"{site['nutrient']}","above threshold" if site["nutrient"]>0.5 else "normal")
    with c3: st.metric("Chlorophyll-a",f"{site['chlorophyll']} μg/L","elevated" if site["chlorophyll"]>3 else "normal")
    with c4: st.metric("Current anomaly",site["current"],"transport risk" if site["risk"]>50 else "low")
    st.markdown(f'<div class="shdr" style="margin-top:18px;">Signal Detection Chain</div>',unsafe_allow_html=True)
    cols=st.columns(4)
    for co,(icon,label,val) in zip(cols,[("🌡","SST rising",site["sst_trend"]),("🧪","Nutrient load",f"Index {site['nutrient']}"),("💨","Wind",site["wind"]),("🌊","Current",site["current"])]):
        with co:
            st.markdown(f'<div style="background:{CARD};border:.5px solid {TEAL2};border-radius:6px;padding:12px;text-align:center;"><div style="font-size:26px;">{icon}</div><div style="color:{WHITE};font-size:12px;font-weight:600;margin-top:4px;">{label}</div><div style="color:{DIM};font-size:11px;margin-top:2px;">{val}</div></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="shdr" style="margin-top:18px;">Sea Surface Temperature — Norwegian Coast</div>',unsafe_allow_html=True)
    st.caption("Heat layer: teal = normal · amber = warm · red = high anomaly · Site markers show HAB risk level")
    st_folium(sst_map(selected_site),width=None,height=420,returned_objects=[])

# ── FORECAST ──────────────────────────────────────────────────────────────────
elif page=="Forecast":
    short=selected_site.split("—")[1].strip()
    st.markdown(f'<h1 style="font-size:26px;margin-bottom:4px;">4-Week HAB Forecast — {short}</h1>',unsafe_allow_html=True)
    st.markdown(f'<p style="color:{DIM};font-size:13px;margin-bottom:16px;">ExplainEarth predictive model · AccEARTH GeoAI · Confidence 85%</p>',unsafe_allow_html=True)
    cc,cs=st.columns([2,1])
    with cc:
        st.markdown(f'<div class="shdr">Probability Forecast</div>',unsafe_allow_html=True)
        st.plotly_chart(forecast_chart(site),use_container_width=True,config={"displayModeBar":False})
    with cs:
        st.markdown(f'<div class="shdr">Week by Week</div>',unsafe_allow_html=True)
        for w,p in zip(["Now","Week 1","Week 2","Week 3","Week 4"],site["weeks"]):
            c=RED if p>=60 else AMBER if p>=40 else TEAL
            st.markdown(f'<div style="background:{CARD};border:.5px solid {TEAL2};border-radius:5px;padding:9px 14px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;"><span style="color:{LIGHT};font-size:13px;">{w}</span><span style="color:{c};font-weight:700;font-size:15px;">{p}%</span></div>',unsafe_allow_html=True)
        exp=site["fish_tonnes"]*4800/1000
        st.markdown(f'<div style="background:{CARD2};border:.5px solid {TEAL};border-radius:6px;padding:14px;margin-top:12px;"><div style="color:{TEAL};font-size:11px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;">Financial exposure</div><div style="color:{WHITE};font-size:22px;font-weight:700;margin-top:4px;">€{exp:.1f}M</div><div style="color:{DIM};font-size:11px;margin-top:2px;">{site["fish_tonnes"]}t biomass · €4,800/t avg value</div></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="shdr" style="margin-top:18px;">Model Input Variables</div>',unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({
        "Variable":["Sea Surface Temperature","Nutrient Load","Chlorophyll-a","Wind Speed","Current Velocity","Historical HAB frequency"],
        "Value":[f"{site['sst']}°C",str(site['nutrient']),f"{site['chlorophyll']} μg/L",site['wind'],site['current'],"4 events / 10 years"],
        "Status":["⚠ Elevated" if site['sst']>12 else "✓ Normal","⚠ High" if site['nutrient']>0.5 else "✓ Normal","⚠ Elevated" if site['chlorophyll']>3 else "✓ Normal","⚠ Active" if site['risk']>50 else "✓ Calm","⚠ Anomaly" if site['risk']>50 else "✓ Normal","⚠ Moderate" if site['risk']>40 else "✓ Low"],
        "Weight":["28%","24%","18%","14%","10%","6%"],
    }),use_container_width=True,hide_index=True)

# ── RECOMMENDATIONS ───────────────────────────────────────────────────────────
elif page=="Recommendations":
    short=selected_site.split("—")[1].strip()
    st.markdown(f'<h1 style="font-size:26px;margin-bottom:4px;">Decision Recommendations — {short}</h1>',unsafe_allow_html=True)
    st.markdown(f'<p style="color:{DIM};font-size:13px;margin-bottom:16px;">ExplainEarth Decision Intelligence · {site["risk"]}% HAB probability</p>',unsafe_allow_html=True)
    sav=site["fish_tonnes"]*4800/1000
    st.markdown(f'<div style="background:{CARD2};border:.5px solid {TEAL};border-radius:8px;padding:18px 24px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;"><div><div style="color:{TEAL};font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">Estimated financial exposure</div><div style="color:{WHITE};font-size:30px;font-weight:700;margin-top:4px;">€{sav:.1f}M</div><div style="color:{DIM};font-size:12px;margin-top:2px;">{site["fish_tonnes"]}t biomass · {site["risk"]}% probability · 4-week window</div></div><div style="text-align:right;"><div style="color:{TEAL};font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">ExplainEarth subscription</div><div style="color:{WHITE};font-size:22px;font-weight:700;margin-top:4px;">€50–200K/yr</div><div style="color:{DIM};font-size:12px;margin-top:2px;">Payback: first alert</div></div></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="shdr">Priority Actions — implement within 72 hours</div>',unsafe_allow_html=True)
    for icon,title,body in [
        ("🚢","Move cages to lower-risk zone",f"Relocate biomass to Site 7 — Sognefjord (28% HAB risk). Cost: €80–120K. Loss avoided: €1.8–3.2M."),
        ("📉","Reduce stocking density immediately","Lower biomass per cage by 30% to reduce environmental stress. Begin within 72 hours."),
        ("⏩","Accelerate harvest schedule",f"Bring forward harvest of {int(site['fish_tonnes']*0.4)}t mature stock. Reduces exposure by ~€{site['fish_tonnes']*0.4*4800/1000:.1f}M."),
    ]:
        st.markdown(f'<div class="rec"><div style="color:{TEAL};font-weight:600;font-size:14px;margin-bottom:4px;">{icon} {title}</div><div style="color:{LIGHT};font-size:13px;">{body}</div></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="shdr" style="margin-top:18px;">Monitoring Actions</div>',unsafe_allow_html=True)
    for icon,title,body in [
        ("📡","Increase sensor frequency","Deploy additional IoT sensors. Increase Copernicus SST pull to 6-hour intervals."),
        ("📋","Notify regulatory authority","Submit early-warning report to Fiskeridirektoratet within 48 hours."),
    ]:
        st.markdown(f'<div class="rec" style="border-left-color:{DIM};"><div style="color:{DIM};font-weight:600;font-size:14px;margin-bottom:4px;">{icon} {title}</div><div style="color:{LIGHT};font-size:13px;">{body}</div></div>',unsafe_allow_html=True)
    st.markdown(f'<div style="background:{CARD};border:.5px solid {TEAL2};border-radius:8px;padding:16px 20px;margin-top:18px;"><div style="color:{TEAL};font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;margin-bottom:8px;">Dual Mission — SDG Alignment</div><p style="color:{LIGHT};font-size:13px;margin:0;">When ExplainEarth prevents this event, it is not just <strong style="color:{WHITE};">€{sav:.1f}M</strong> recovered. It is <strong style="color:{TEAL};">{site["fish_tonnes"]}t of food</strong>, ocean biomass, and years of natural growth returned to people and planet.</p><p style="color:{DIM};font-size:12px;margin:8px 0 0;">SDG 2 Zero Hunger · SDG 12 Responsible Consumption · SDG 13 Climate Action · SDG 14 Life Below Water</p></div>',unsafe_allow_html=True)

# ── ABOUT ─────────────────────────────────────────────────────────────────────
elif page=="About":
    st.markdown(f'<h1 style="font-size:26px;margin-bottom:20px;">About ExplainEarth</h1>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown(f'<div style="background:{CARD};border:.5px solid {TEAL2};border-radius:8px;padding:20px 24px;margin-bottom:16px;"><div style="color:{TEAL};font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;margin-bottom:10px;">Our Mission</div><p style="color:{LIGHT};font-size:14px;line-height:1.7;margin:0;">ExplainEarth is an AI-powered <strong style="color:{WHITE};">Environmental Decision Intelligence Platform</strong> with a dual mission: protect the financial value of industries — and preserve the physical resources behind that value. When a €200M aquaculture loss is avoided, it is not just money recovered. It is food, ocean biomass, and years of natural growth returned to people and planet.</p></div>',unsafe_allow_html=True)
        layers="".join([f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;"><div style="background:{TEAL};color:{BG};font-weight:700;font-size:12px;border-radius:4px;width:22px;height:22px;min-width:22px;display:flex;align-items:center;justify-content:center;">{n}</div><div><div style="color:{WHITE};font-size:13px;font-weight:600;">{t}</div><div style="color:{DIM};font-size:11px;">{s}</div></div></div>' for n,t,s in [("4","Decision Intelligence","What to do — actionable recommendations"),("3","Future Intelligence","What will happen — 4-week forecast"),("2","GeoAI","Why it is happening — environmental risk models"),("1","Earth Intelligence","What is happening — real-time Earth data")]])
        st.markdown(f'<div style="background:{CARD};border:.5px solid {TEAL2};border-radius:8px;padding:20px 24px;"><div style="color:{TEAL};font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;margin-bottom:12px;">Four Intelligence Layers</div>{layers}</div>',unsafe_allow_html=True)
    with c2:
        ds="".join([f'<div style="background:{CARD2};border-radius:4px;padding:8px 12px;margin-bottom:6px;color:{LIGHT};font-size:13px;">{d}</div>' for d in ["🛰 Copernicus Marine Service (CMEMS)","🛰 ESA Sentinel Earth Observation","🌊 NOAA Ocean Data","🌤 MET Norway Weather API","📡 IoT Sensor Networks (in development)"]])
        st.markdown(f'<div style="background:{CARD};border:.5px solid {TEAL2};border-radius:8px;padding:20px 24px;margin-bottom:16px;"><div style="color:{TEAL};font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;margin-bottom:12px;">Data Stack</div>{ds}</div>',unsafe_allow_html=True)
        st.markdown(f'<div style="background:{CARD};border:.5px solid {TEAL2};border-radius:8px;padding:20px 24px;"><div style="color:{TEAL};font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;margin-bottom:12px;">Founder</div><div style="color:{WHITE};font-size:15px;font-weight:600;">Dr. Tamer Abu-Alam</div><div style="color:{TEAL};font-size:12px;margin-bottom:10px;">Founder & CEO, ExplainEarth (in formation)</div><div style="color:{DIM};font-size:12px;line-height:1.65;">25+ years Earth science · AI & sustainability analytics · €28M+ innovation portfolio · 65+ peer-reviewed papers · CloudEARTHi founder — 50+ organisations across 13 countries</div></div>',unsafe_allow_html=True)
    st.markdown(f'<div style="background:{CARD2};border:.5px solid {TEAL};border-radius:8px;padding:16px 24px;margin-top:16px;text-align:center;"><span style="color:{TEAL};font-style:italic;font-size:15px;font-weight:500;">"The Earth is already sending the signals. ExplainEarth will make them actionable."</span></div>',unsafe_allow_html=True)
