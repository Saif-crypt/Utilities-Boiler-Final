# boiler_dashboard_final.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt

# Ensure non-interactive backend (safe on servers)
plt.switch_backend("Agg")

# Page config
st.set_page_config(page_title="Boiler Performance Dashboard", page_icon="🔥", layout="wide")

# ---------- Custom CSS ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Roboto+Mono:wght@400;700&display=swap');

    :root {
      --accent: #1E88E5;
      --muted: #9aa6b2;
      --card-bg: rgba(255,255,255,0.02);
    }

    .reportview-container .main { font-family: 'Inter', sans-serif; color: #e6eef6; }
    .header { display:flex; gap:12px; align-items:center; justify-content:space-between; margin-bottom:12px; }
    .title { font-size: 28px; font-weight:700; color:var(--accent); }
    .subtitle { font-family: 'Roboto Mono', monospace; color:var(--muted); font-size:12px; }

    /* KPI card */
    .kpi-card {
      background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border-radius:12px; padding:14px; box-shadow:0 6px 18px rgba(2,6,23,0.5);
      border:1px solid rgba(255,255,255,0.03);
      min-height:120px;
    }
    .kpi-title { margin:0; color:#cbd5e1; font-size:14px; }
    .kpi-value { font-size:20px; font-weight:700; color:white; margin-top:6px; }
    .kpi-delta { font-size:12px; color:#9ee7a9; margin-top:4px; }
    .kpi-sublabel { font-size:12px; color:var(--muted); margin-top:4px; }

    .divider { height:1px; background: rgba(255,255,255,0.03); margin:18px 0; border-radius:2px; }

    /* make dataframe look nice */
    .stDataFrame table { border-radius: 8px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
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
        "Steam_Output": base_fuel * 2.5 + np.random.normal(0, 50, len(dates)),
    }
    return pd.DataFrame(data)

# ---------- Sidebar controls ----------
with st.sidebar:
    st.header("⚙️ Controls")
    start_date = st.date_input("Start", value=datetime(2025, 9, 1))
    end_date = st.date_input("End", value=datetime(2025, 10, 3))
    show_trendline = st.checkbox("Show trendlines (OLS)", value=True)
    st.checkbox("Dark mode (UI hint)", value=True)
    with st.expander("Advanced"):
        st.checkbox("Show raw table by default", value=False)
        st.selectbox("Chart palette", ["Viridis", "Turbo", "Blues"], index=0)
    st.markdown("---")
    if st.button("🔄 Refresh data"):
        st.experimental_rerun()

# ---------- Load and filter ----------
df = generate_sample_data()
mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
filtered_df = df.loc[mask].copy()

if filtered_df.empty:
    st.warning("No data available for the selected date range.")
    st.stop()

# ---------- Header ----------
left, right = st.columns([4, 1])
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
        unsafe_allow_html=True,
    )
with right:
    st.metric(label="Records", value=len(filtered_df))

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------- Helper: PNG sparkline via matplotlib (tight, transparent) ----------
def sparkline_png(series, width_px=360, height_px=48, line_color="#8fd3ff"):
    """
    Return PNG bytes for a tiny sparkline for use with st.image.
    Transparent background, no axes, tight margins.
    """
    y = np.array(series)
    fig = plt.figure(figsize=(width_px / 100, height_px / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.plot(y, linewidth=1.6, color=line_color)
    ax.set_axis_off()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

# ---------- KPIs: single tidy card per column (NO empty boxes) ----------
kpi_cols = st.columns(4, gap="large")

# Average Efficiency card
with kpi_cols[0]:
    with st.container():
        st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
        avg_eff = filtered_df["Efficiency_X"].mean()
        prev_avg = (
            df.loc[df["Date"] < filtered_df["Date"].min(), "Efficiency_X"].mean()
            if not df.loc[df["Date"] < filtered_df["Date"].min()].empty
            else avg_eff
        )
        delta = avg_eff - (prev_avg if not np.isnan(prev_avg) else avg_eff)
        st.markdown("<div class='kpi-title'>Average Efficiency</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-value'>{avg_eff:.1f}%</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-delta'>{delta:+.2f}% vs prev</div>", unsafe_allow_html=True)
        img_bytes = sparkline_png(filtered_df["Efficiency_X"], width_px=360, height_px=48, line_color="#8fd3ff")
        st.image(img_bytes, use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Total Fuel card
with kpi_cols[1]:
    with st.container():
        st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
        total_fuel = filtered_df["Total_Fuel_Corrected"].sum()
        prev_fuel = (
            df.loc[df["Date"] < filtered_df["Date"].min(), "Total_Fuel_Corrected"].sum()
            if not df.loc[df["Date"] < filtered_df["Date"].min()].empty
            else total_fuel
        )
        delta_fuel = total_fuel - prev_fuel
        st.markdown("<div class='kpi-title'>Total Fuel</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-value'>{total_fuel:.0f} units</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-delta'>{delta_fuel:+.0f} units vs prev</div>", unsafe_allow_html=True)
        img_bytes = sparkline_png(filtered_df["Total_Fuel_Corrected"], width_px=360, height_px=48, line_color="#9fe2a6")
        st.image(img_bytes, use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Avg Temp card
with kpi_cols[2]:
    with st.container():
        st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
        avg_temp = filtered_df["Temperature"].mean()
        st.markdown("<div class='kpi-title'>Avg Temp</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-value'>{avg_temp:.1f}°C</div>", unsafe_allow_html=True)
        st.markdown("<div class='kpi-sublabel'>Operational average</div>", unsafe_allow_html=True)
        img_bytes = sparkline_png(filtered_df["Temperature"], width_px=360, height_px=48, line_color="#ffd28f")
        st.image(img_bytes, use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Avg Pressure card
with kpi_cols[3]:
    with st.container():
        st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
        avg_pres = filtered_df["Pressure"].mean()
        st.markdown("<div class='kpi-title'>Avg Pressure</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kpi-value'>{avg_pres:.1f} kPa</div>", unsafe_allow_html=True)
        st.markdown("<div class='kpi-sublabel'>Mean operating pressure</div>", unsafe_allow_html=True)
        img_bytes = sparkline_png(filtered_df["Pressure"], width_px=360, height_px=48, line_color="#9bd1ff")
        st.image(img_bytes, use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------- Main charts ----------
c1, c2 = st.columns([2, 1])

with c1:
    try:
        fig = px.scatter(
            filtered_df,
            x="Total_Fuel_Corrected",
            y="Efficiency_X",
            color="Efficiency_X",
            color_continuous_scale="Viridis",
            labels={"Total_Fuel_Corrected": "Fuel (units)", "Efficiency_X": "Efficiency (%)"},
            trendline="ols" if show_trendline else None,
            title="Fuel vs Efficiency",
        )
        fig.update_layout(height=440, margin=dict(t=40))
        fig.update_traces(marker=dict(size=8, opacity=0.9))
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.error("Trendline requires statsmodels. Showing scatter without trendline.")
        fig = px.scatter(filtered_df, x="Total_Fuel_Corrected", y="Efficiency_X", title="Fuel vs Efficiency")
        st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.histogram(filtered_df, x="Efficiency_X", nbins=12, title="Efficiency distribution")
    fig.update_layout(height=440, margin=dict(t=40))
    st.plotly_chart(fig, use_container_width=True)

# ---------- Time series ----------
st.markdown("---")
st.subheader("Time Series Analysis")
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
st.markdown("---")
st.subheader("Correlation matrix")
numeric_df = filtered_df.select_dtypes(include=[np.number])
corr_matrix = numeric_df.corr()
fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlation between metrics")
fig.update_layout(height=350)
st.plotly_chart(fig, use_container_width=True)

# ---------- Export buttons (SAFE: placed AFTER filtered_df exists) ----------
st.markdown("---")
st.sidebar.markdown("## Export")

csv_str = filtered_df.to_csv(index=False)
st.sidebar.download_button(
    label="📥 Download filtered CSV",
    data=csv_str,
    file_name="boiler_filtered.csv",
    mime="text/csv",
)

csv_bytes = csv_str.encode("utf-8")
st.sidebar.download_button(
    label="📥 Download CSV (utf-8)",
    data=csv_bytes,
    file_name="boiler_filtered_utf8.csv",
    mime="text/csv",
)

# Excel (.xlsx) — safe try/except: only attempt if engine available
try:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        filtered_df.to_excel(writer, index=False, sheet_name="Filtered")
    buffer.seek(0)
    excel_data = buffer.getvalue()
    st.sidebar.download_button(
        label="📥 Download Excel (.xlsx)",
        data=excel_data,
        file_name="boiler_filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
except Exception:
    st.sidebar.info("Excel export requires 'openpyxl' installed. Use pip install openpyxl if needed.")

# ---------- KEY STATISTICS (moved to bottom, full-width & expanded) ----------
st.markdown("---")
st.subheader("Key Statistics (Full summary)")
st.markdown(
    "This summary expands to fill the content area. Use it to quickly copy / check central moments."
)
st.dataframe(filtered_df[["Efficiency_X", "Total_Fuel_Corrected", "Temperature", "Pressure"]].describe(), use_container_width=True)

# ---------- Raw data ----------
if st.sidebar.checkbox("Show raw data", value=False):
    st.subheader("Raw data")
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
