import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page config
st.set_page_config(page_title="Boiler Performance Dashboard", page_icon="🔥", layout="wide")

# ---------- Custom CSS (glass + fonts + dark) ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Roboto+Mono:wght@400;700&display=swap');

    :root {
      --accent: #1E88E5;
      --bg: #0f1724;
      --card: rgba(255,255,255,0.03);
      --glass: rgba(255,255,255,0.04);
      --muted: #9aa6b2;
    }

    /* body */
    .reportview-container .main {
        font-family: 'Inter', sans-serif;
    }

    /* Header */
    .header {
      display: flex;
      align-items:center;
      gap: 12px;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .title {
      font-size: 28px;
      font-weight: 700;
      color: var(--accent);
      display:flex;
      align-items:center;
      gap:10px;
    }
    .subtitle {
      font-family: 'Roboto Mono', monospace;
      color: var(--muted);
      font-size: 12px;
    }

    /* KPI glass card */
    .kpi {
      background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border-radius: 12px;
      padding: 14px;
      box-shadow: 0 6px 18px rgba(2,6,23,0.5);
      border: 1px solid rgba(255,255,255,0.03);
    }
    .kpi h4 { margin:0; color:#cbd5e1; font-size:12px; }
    .kpi .value { font-size:20px; font-weight:700; color: white; margin-top:6px; }
    .kpi .delta { font-size:12px; color: #9ee7a9; margin-top:4px; }

    /* small text and divider */
    .muted { color: var(--muted); font-size:13px; }
    .divider { height:1px; background: rgba(255,255,255,0.03); margin:12px 0; border-radius:2px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Sample data generator ----------
@st.cache_data
def generate_sample_data():
    dates = pd.date_range(start="2025-09-01", end="2025-10-03", freq="D")
    np.random.seed(42)
    base_fuel = np.random.uniform(100, 500, len(dates))
    efficiency = 85 - (base_fuel - 300) ** 2 / 8000 + np.random.normal(0, 3, len(dates))
    efficiency = np.clip(efficiency, 65, 95)
    data = {
        "Date": dates,
        "Total_Fuel_Corrected": base_fuel,
        "Efficiency_X": efficiency,
        "Temperature": np.random.uniform(60, 120, len(dates)),
        "Pressure": np.random.uniform(10, 50, len(dates)),
        "Operating_Hours": np.random.uniform(8, 24, len(dates)),
        "Steam_Output": base_fuel * 2.5 + np.random.normal(0, 50, len(dates))
    }
    return pd.DataFrame(data)

# ---------- Sidebar controls ----------
with st.sidebar:
    st.header("⚙️ Controls")
    today = datetime.now()
    start_date = st.date_input("Start", value=datetime(2025, 9, 1))
    end_date = st.date_input("End", value=datetime(2025, 10, 3))
    show_trendline = st.checkbox("Show trendlines (OLS)", value=True)
    dark_mode = st.checkbox("Dark mode (UI hint)", value=True)
    with st.expander("Advanced"):
        st.checkbox("Show raw table by default", value=False)
        st.selectbox("Chart palette", ["Viridis", "Turbo", "Blues"], index=0)
    st.markdown("---")
    if st.button("🔄 Refresh data"):
        st.experimental_rerun()
    st.markdown("### Export")
    # -- CSV download (string) --
csv_str = filtered_df.to_csv(index=False)
st.download_button(
    label="Download filtered CSV",
    data=csv_str,
    file_name="boiler_filtered.csv",
    mime="text/csv"
)


# ---------- Load and filter ----------
df = generate_sample_data()
mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
filtered_df = df.loc[mask].copy()
if filtered_df.empty:
    st.warning("No data for selected date range.")
    st.stop()

# ---------- Header ----------
left, right = st.columns([4,1])
with left:
    st.markdown(
        f"""
        <div class="header">
            <div>
                <div class="title">🔥 Boiler Performance Dashboard</div>
                <div class="subtitle">Plant: Refrigeration Plant  •  Boiler ID: B-02  •  Last update: {df['Date'].max().date()}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with right:
    st.metric(label="Records", value=len(filtered_df), delta=f"{len(filtered_df) - len(df):+d}")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------- KPIs with small sparklines ----------
kpi_cols = st.columns(4)
# helper to make sparkline fig and return html
def sparkline(series):
    fig = px.line(series.reset_index(), x='index', y=series.name, height=50)
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig

# KPI 1: avg efficiency
with kpi_cols[0]:
    avg_eff = filtered_df['Efficiency_X'].mean()
    prev_avg = df.loc[df['Date'] < filtered_df['Date'].min(), 'Efficiency_X'].mean() if not df.loc[df['Date'] < filtered_df['Date'].min()].empty else avg_eff
    delta = avg_eff - (prev_avg if not np.isnan(prev_avg) else avg_eff)
    st.markdown("<div class='kpi'>", unsafe_allow_html=True)
    st.markdown(f"<h4>Average Efficiency</h4>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{avg_eff:.1f}%</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='delta'>{delta:+.2f}% vs prev</div>", unsafe_allow_html=True)
    fig = sparkline(filtered_df['Efficiency_X'])
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# KPI 2: total fuel
with kpi_cols[1]:
    total_fuel = filtered_df['Total_Fuel_Corrected'].sum()
    prev_fuel = df.loc[df['Date'] < filtered_df['Date'].min(), 'Total_Fuel_Corrected'].sum() if not df.loc[df['Date'] < filtered_df['Date'].min()].empty else total_fuel
    delta_fuel = total_fuel - prev_fuel
    st.markdown("<div class='kpi'>", unsafe_allow_html=True)
    st.markdown(f"<h4>Total Fuel</h4>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{total_fuel:.0f} units</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='delta'>{delta_fuel:+.0f} units vs prev</div>", unsafe_allow_html=True)
    fig = sparkline(filtered_df['Total_Fuel_Corrected'])
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# KPI 3: avg temp
with kpi_cols[2]:
    avg_temp = filtered_df['Temperature'].mean()
    st.markdown("<div class='kpi'>", unsafe_allow_html=True)
    st.markdown(f"<h4>Avg Temp</h4>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{avg_temp:.1f}°C</div>", unsafe_allow_html=True)
    fig = sparkline(filtered_df['Temperature'])
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# KPI 4: avg pressure
with kpi_cols[3]:
    avg_pres = filtered_df['Pressure'].mean()
    st.markdown("<div class='kpi'>", unsafe_allow_html=True)
    st.markdown(f"<h4>Avg Pressure</h4>", unsafe_allow_html=True)
    st.markdown(f"<div class='value'>{avg_pres:.1f} kPa</div>", unsafe_allow_html=True)
    fig = sparkline(filtered_df['Pressure'])
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------- Main charts ----------
c1, c2 = st.columns([2,1])

with c1:
    # scatter with optional trendline
    try:
        fig = px.scatter(
            filtered_df,
            x="Total_Fuel_Corrected",
            y="Efficiency_X",
            color="Efficiency_X",
            color_continuous_scale="Viridis",
            labels={"Total_Fuel_Corrected": "Fuel (units)", "Efficiency_X": "Efficiency (%)"},
            trendline="ols" if show_trendline else None,
            title="Fuel vs Efficiency"
        )
        fig.update_layout(height=440, margin=dict(t=40))
        fig.update_traces(marker=dict(size=8, opacity=0.9))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error("Trendline requires statsmodels. Showing scatter without trendline.")
        fig = px.scatter(filtered_df, x="Total_Fuel_Corrected", y="Efficiency_X", title="Fuel vs Efficiency")
        st.plotly_chart(fig, use_container_width=True)

with c2:
    # histogram + distribution
    fig = px.histogram(filtered_df, x="Efficiency_X", nbins=12, title="Efficiency distribution")
    fig.update_layout(height=440, margin=dict(t=40))
    st.plotly_chart(fig, use_container_width=True)

# ---------- Time series ----------
st.subheader("Time series")
ts1, ts2 = st.columns(2)
with ts1:
    fig = px.line(filtered_df, x="Date", y="Efficiency_X", title="Efficiency over time")
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)
with ts2:
    fig = px.line(filtered_df, x="Date", y="Total_Fuel_Corrected", title="Fuel consumption over time")
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Correlation ----------
st.subheader("Correlation matrix")
numeric_df = filtered_df.select_dtypes(include=[np.number])
corr_matrix = numeric_df.corr()
fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlation between metrics")
fig.update_layout(height=350)
st.plotly_chart(fig, use_container_width=True)

# ---------- Raw data (optional) ----------
if st.sidebar.checkbox("Show raw data", value=False):
    st.subheader("Raw data")
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
