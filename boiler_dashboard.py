# boiler_dashboard_no_pills.py
# Screenshot (for reference): /mnt/data/a3975c91-e3c9-4fb0-a984-4910e9bfad62.png

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
    }

    .reportview-container .main { font-family: 'Inter', sans-serif; color: #e6eef6; }
    .header { display:flex; gap:12px; align-items:center; justify-content:space-between; margin-bottom:12px; }
    .title { font-size: 28px; font-weight:700; color:var(--accent); }
    .subtitle { font-family: 'Roboto Mono', monospace; color:var(--muted); font-size:12px; }

    .kpi { background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
           border-radius:12px; padding:14px; box-shadow:0 6px 18px rgba(2,6,23,0.5);
           border:1px solid rgba(255,255,255,0.03); min-height:120px; }
    .kpi h4 { margin:0; color:#cbd5e1; font-size:14px; }
    .kpi .value { font-size:20px; font-weight:700; color:white; margin-top:6px; }
    .kpi .delta { font-size:12px; color:#9ee7a9; margin-top:4px; margin-bottom: 8px; }
    .muted { color: var(--muted); font-size:13px; }
    .divider { height:1px; background: rgba(255,255,255,0.03); margin:18px 0; border-radius:2px; }
    
    /* Sparkline container styling - FIXED */
    .sparkline-container {
        height: 35px;
        width: 100%;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 4px;
    }
    
    /* Fix for plotly charts inside containers */
    .kpi .stPlotlyChart {
        margin-top: 0px;
        margin-bottom: 0px;
    }
    
    /* Statistics section styling */
    .stats-section {
        background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.03);
        margin-top: 20px;
    }
    
    /* Remove extra spacing around plotly charts */
    .js-plotly-plot .plotly .main-svg {
        border-radius: 4px;
    }

    /* === ADDED RULES TO FORCE SPARKLINES INSIDE KPI BOXES ===
       This is the only functional change: it removes the extra
       padding/margins Streamlit adds and clamps the chart height so
       the tiny sparklines remain fully inside the `.kpi` card.
    */
    .kpi .element-container {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        margin-top: -8px !important;
        margin-bottom: -10px !important;
    }

    .kpi .stPlotlyChart {
        height: 35px !important;
        overflow: hidden !important;
    }

    /* In case Streamlit wraps charts in other divs, extra safety */
    .kpi iframe, .kpi div[data-testid="stPlotlyChart"] {
        height: 35px !important;
        min-height: 35px !important;
        max-height: 35px !important;
        overflow: hidden !important;
    }

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
        st.rerun()

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

# ---------- Improved sparkline function ----------
def create_sparkline_figure(series, line_color="#8fd3ff", height=35):
    """Create a minimal sparkline using plotly"""
    fig = px.line(
        y=series.values,
        line_shape="spline",
        height=height
    )
    fig.update_traces(
        line=dict(color=line_color, width=2),
        showlegend=False
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        hovermode=False,
        showlegend=False
    )
    return fig

# ---------- KPIs (Fixed - sparklines inside boxes) ----------
kpi_cols = st.columns(4)

with kpi_cols[0]:
    avg_eff = filtered_df["Efficiency_X"].mean()
    prev_avg = (
        df.loc[df["Date"] < filtered_df["Date"].min(), "Efficiency_X"].mean()
        if not df.loc[df["Date"] < filtered_df["Date"].min()].empty
        else avg_eff
    )
    delta = avg_eff - (prev_avg if not np.isnan(prev_avg) else avg_eff)
    
    # Create container for the entire KPI card
    with st.container():
        st.markdown(f"""
        <div class='kpi'>
            <h4>Average Efficiency</h4>
            <div class='value'>{avg_eff:.1f}%</div>
            <div class='delta'>{delta:+.2f}% vs prev</div>
            <div class='sparkline-container'>
        """, unsafe_allow_html=True)
        
        # Sparkline inside the card
        sparkline_fig = create_sparkline_figure(filtered_df["Efficiency_X"], line_color="#8fd3ff")
        st.plotly_chart(sparkline_fig, use_container_width=True, config={'displayModeBar': False}, key="spark_eff")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

with kpi_cols[1]:
    total_fuel = filtered_df["Total_Fuel_Corrected"].sum()
    prev_fuel = (
        df.loc[df["Date"] < filtered_df["Date"].min(), "Total_Fuel_Corrected"].sum()
        if not df.loc[df["Date"] < filtered_df["Date"].min()].empty
        else total_fuel
    )
    delta_fuel = total_fuel - prev_fuel
    
    with st.container():
        st.markdown(f"""
        <div class='kpi'>
            <h4>Total Fuel</h4>
            <div class='value'>{total_fuel:.0f} units</div>
            <div class='delta'>{delta_fuel:+.0f} units vs prev</div>
            <div class='sparkline-container'>
        """, unsafe_allow_html=True)
        
        sparkline_fig = create_sparkline_figure(filtered_df["Total_Fuel_Corrected"], line_color="#9fe2a6")
        st.plotly_chart(sparkline_fig, use_container_width=True, config={'displayModeBar': False}, key="spark_fuel")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

with kpi_cols[2]:
    avg_temp = filtered_df["Temperature"].mean()
    
    with st.container():
        st.markdown(f"""
        <div class='kpi'>
            <h4>Avg Temp</h4>
            <div class='value'>{avg_temp:.1f}°C</div>
            <div class='delta'>&nbsp;</div>
            <div class='sparkline-container'>
        """, unsafe_allow_html=True)
        
        sparkline_fig = create_sparkline_figure(filtered_df["Temperature"], line_color="#ffd28f")
        st.plotly_chart(sparkline_fig, use_container_width=True, config={'displayModeBar': False}, key="spark_temp")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

with kpi_cols[3]:
    avg_pres = filtered_df["Pressure"].mean()
    
    with st.container():
        st.markdown(f"""
        <div class='kpi'>
            <h4>Avg Pressure</h4>
            <div class='value'>{avg_pres:.1f} kPa</div>
            <div class='delta'>&nbsp;</div>
            <div class='sparkline-container'>
        """, unsafe_allow_html=True)
        
        sparkline_fig = create_sparkline_figure(filtered_df["Pressure"], line_color="#9bd1ff")
        st.plotly_chart(sparkline_fig, use_container_width=True, config={'displayModeBar': False}, key="spark_pres")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

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

# ---------- Expanded Key Statistics at the bottom ----------
st.markdown("---")
st.markdown("<div class='stats-section'>", unsafe_allow_html=True)
st.subheader("📊 Detailed Statistics Summary")

# Create expanded statistics
stats_cols = st.columns(4)

with stats_cols[0]:
    st.markdown("**Efficiency Statistics**")
    eff_stats = filtered_df["Efficiency_X"].describe()
    st.metric("Mean", f"{eff_stats['mean']:.1f}%")
    st.metric("Std Dev", f"{eff_stats['std']:.1f}%")
    st.metric("Min", f"{eff_stats['min']:.1f}%")
    st.metric("Max", f"{eff_stats['max']:.1f}%")

with stats_cols[1]:
    st.markdown("**Fuel Statistics**")
    fuel_stats = filtered_df["Total_Fuel_Corrected"].describe()
    st.metric("Mean", f"{fuel_stats['mean']:.0f} units")
    st.metric("Std Dev", f"{fuel_stats['std']:.0f} units")
    st.metric("Min", f"{fuel_stats['min']:.0f} units")
    st.metric("Max", f"{fuel_stats['max']:.0f} units")

with stats_cols[2]:
    st.markdown("**Temperature Statistics**")
    temp_stats = filtered_df["Temperature"].describe()
    st.metric("Mean", f"{temp_stats['mean']:.1f}°C")
    st.metric("Std Dev", f"{temp_stats['std']:.1f}°C")
    st.metric("Min", f"{temp_stats['min']:.1f}°C")
    st.metric("Max", f"{temp_stats['max']:.1f}°C")

with stats_cols[3]:
    st.markdown("**Pressure Statistics**")
    pressure_stats = filtered_df["Pressure"].describe()
    st.metric("Mean", f"{pressure_stats['mean']:.1f} kPa")
    st.metric("Std Dev", f"{pressure_stats['std']:.1f} kPa")
    st.metric("Min", f"{pressure_stats['min']:.1f} kPa")
    st.metric("Max", f"{pressure_stats['max']:.1f} kPa")

# Additional statistics in an expander
with st.expander("View Complete Statistical Summary Table"):
    st.dataframe(filtered_df[["Efficiency_X", "Total_Fuel_Corrected", "Temperature", "Pressure", "Operating_Hours", "Steam_Output"]].describe(), use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

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

# ---------- Raw data ----------
if st.sidebar.checkbox("Show raw data", value=False):
    st.subheader("Raw data")
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
