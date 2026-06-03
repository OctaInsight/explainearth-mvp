# ExplainEarth MVP
**Environmental Decision Intelligence Platform**
*Dr. Tamer Abu-Alam — Founder & CEO*

---

## Deploy to Streamlit Cloud (5 minutes)

### Step 1 — Create a GitHub repository
1. Go to github.com and create a new **public** repository
2. Name it: `explainearth-mvp`
3. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`

### Step 2 — Deploy on Streamlit Cloud
1. Go to **share.streamlit.io**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your `explainearth-mvp` repository
5. Main file path: `app.py`
6. Click **"Deploy"**

### Step 3 — Get your link
Streamlit Cloud will give you a public URL like:
`https://explainearth-mvp.streamlit.app`

This is the link you paste into the EWOR application form.

---

## What the MVP shows

| Page | Content |
|---|---|
| **Overview** | Map of Norwegian coast with 4 monitoring sites, risk alerts, live metrics |
| **HAB Risk Monitor** | Real-time environmental signals, SST heatmap, alert severity |
| **Forecast** | 4-week HAB probability chart, financial exposure calculation |
| **Recommendations** | Three priority actions with cost/benefit analysis, SDG alignment |
| **About** | ExplainEarth mission, four-layer architecture, founder profile |

---

## Local testing (optional)
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

*ExplainEarth — The Earth is already sending the signals. We make them actionable.*
