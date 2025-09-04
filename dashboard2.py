import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Boiler Plant Dashboard", layout="wide", page_icon="🔥")
st.markdown("<style>footer {visibility: hidden;} .big-metric {font-size: 2rem;} </style>", unsafe_allow_html=True)

# --- COOL SIDEBAR START ---
with st.sidebar:
    st.markdown(
        """
        <style>
        .sidebar-title {
            font-size: 22px !important;
            font-weight: bold;
            color: #FF4B4B;
        }
        .sidebar-sub {
            font-size: 14px !important;
            color: #888;
        }
        .sidebar-divider {
            border-top: 1px solid #444;
            margin: 10px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.image("https://img.icons8.com/emoji/96/fire.png", width=60)
    st.markdown('<p class="sidebar-title">Boiler Plant Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-sub">Monitor 🔥 Efficiency, ⚡ Output, ⛽ Fuel & 📊 Trends</p>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Sidebar filters
    boiler_choice = st.radio("Select Boiler", ["All Boilers", "Boiler 1", "Boiler 2"], index=0)
    date_range = st.date_input("📅 Select Date Range", [])
    shift = st.selectbox("🕒 Shift", ["All", "Morning", "Evening", "Night"])

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.info("💡 Tip: Use filters to analyze boiler-specific KPIs", icon="ℹ️")
    st.caption("⚙️ Developed by Your Team | Powered by Streamlit")

    
    # Logo / Icon
    st.image("https://img.icons8.com/emoji/96/fire.png", width=60)
    st.markdown('<p class="sidebar-title">Boiler Plant Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-sub">Monitor 🔥 Efficiency, ⚡ Output, ⛽ Fuel & 📊 Trends</p>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Boiler selection
    boiler_choice = st.radio("Select Boiler", ["All Boilers", "Boiler 1", "Boiler 2"], index=0)

    # Date filter
    st.date_input("📅 Select Date Range", [])

    # Shift selection
    shift = st.selectbox("🕒 Shift", ["All", "Morning", "Evening", "Night"])

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Info card
    st.info("💡 Tip: Use filters to analyze boiler-specific KPIs", icon="ℹ️")

    # Footer
    st.caption("⚙️ Developed by Your Team | Powered by Streamlit")
# --- COOL SIDEBAR END ---


CSV_PATH = "boiler_phase3_dashboard.csv"  # Or upload/file selector if desired
df = pd.read_csv(CSV_PATH)

# Make a working copy for filtering
df_filtered = df.copy()

# Apply boiler filter
if boiler_choice == "Boiler 1":
    df_filtered["Total_Fuel_m3"] = df[b1_fuel]
    df_filtered["Total_Steam_Tons"] = df[b1_steam]
elif boiler_choice == "Boiler 2":
    df_filtered["Total_Fuel_m3"] = df[b2_fuel]
    df_filtered["Total_Steam_Tons"] = df[b2_steam]
# if "All Boilers", keep totals (already calculated)

# Apply date filter if timestamp exists
if ts_col and len(date_range) == 2:
    start, end = pd.to_datetime(date_range)
    df_filtered = df_filtered[(df_filtered[ts_col] >= start) & (df_filtered[ts_col] <= end)]

# Apply shift filter (⚠️ only works if your dataset has a "Shift" column)
if "Shift" in df_filtered.columns and shift != "All":
    df_filtered = df_filtered[df_filtered["Shift"] == shift]


def pick(names):
    return next((n for n in names if n in df.columns), None)

ts_col   = pick(["Timestamp", "timestamp", "Date", "Datetime"])
b1_fuel  = pick(["Boiler1_FuelConsumption_m3", "Boiler1_Fuel_m3", "B1_Fuel_m3"])
b2_fuel  = pick(["Boiler2_FuelConsumption_m3", "Boiler2_Fuel_m3", "B2_Fuel_m3"])
b1_steam = pick(["Boiler1_Steam_Tons", "Boiler1_Steam_Ton", "B1_Steam_Tons"])
b2_steam = pick(["Boiler2_Steam_Tons", "Boiler2_Steam_Ton", "B2_Steam_Tons"])
eff_col  = pick(["Overall_Efficiency_%", "Efficiency_Pred", "Boiler_Efficiency"])
o2_col   = pick(["O2_Percent", "Boiler1_O2_%", "O2_%"])

missing_core = [n for n,v in {
    "Boiler1 fuel": b1_fuel,
    "Boiler2 fuel": b2_fuel,
    "Boiler1 steam": b1_steam,
    "Boiler2 steam": b2_steam
}.items() if v is None]
if missing_core:
    st.error("Missing required columns: " + ", ".join(missing_core))
    st.stop()

if ts_col:
    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
df["Total_Fuel_m3"] = df[b1_fuel].fillna(0) + df[b2_fuel].fillna(0)
df["Total_Steam_Tons"] = df[b1_steam].fillna(0) + df[b2_steam].fillna(0)
if eff_col is None:
    df["Overall_Efficiency_%"] = (df["Total_Steam_Tons"] / df["Total_Fuel_m3"].replace(0, np.nan)) * 100
    eff_col = "Overall_Efficiency_%"

# ---- Fancier KPIs ----
c1, c2, c3 = st.columns(3)
c1.metric("Total Fuel (m³)", f"{df['Total_Fuel_m3'].sum():,.0f}",
          delta=f"{df['Total_Fuel_m3'].diff().iloc[-1]:+.0f}" if len(df) > 1 else None)
c2.metric("Total Steam (tons)", f"{df['Total_Steam_Tons'].sum():,.0f}",
          delta=f"{df['Total_Steam_Tons'].diff().iloc[-1]:+.0f}" if len(df) > 1 else None)
c3.metric("Avg Efficiency (%)", f"{df[eff_col].mean():.2f}",
          delta=f"{df[eff_col].diff().iloc[-1]:+.2f}" if len(df) > 1 else None)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Trends",
    "⚡ Efficiency vs O₂",
    "🛠 Boiler Comparison",
    "🌡️ Heatmap"])

with tab1:
    st.subheader("Fuel & Steam Over Time")
    if ts_col:
        df_trend = df.copy().set_index(ts_col).sort_index()
        df_trend["Fuel_roll"] = df_trend["Total_Fuel_m3"].rolling(3, min_periods=1).mean()
        df_trend["Steam_roll"] = df_trend["Total_Steam_Tons"].rolling(3, min_periods=1).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_trend.index, y=df_trend["Total_Fuel_m3"], mode='lines+markers',
                                 name="Total Fuel (m³)", line=dict(width=2, color='firebrick')))
        fig.add_trace(go.Scatter(x=df_trend.index, y=df_trend["Fuel_roll"], mode='lines',
                                 name="Fuel (3pt MA)", line=dict(width=2, dash='dot', color='orange')))
        fig.add_trace(go.Scatter(x=df_trend.index, y=df_trend["Total_Steam_Tons"], mode='lines+markers',
                                 name="Total Steam (t)", yaxis='y2', line=dict(width=2, color='steelblue')))
        fig.add_trace(go.Scatter(x=df_trend.index, y=df_trend["Steam_roll"], mode='lines',
                                 name="Steam (3pt MA)", yaxis='y2', line=dict(width=2, dash='dot', color='deepskyblue')))
        fig.update_layout(
            xaxis_title="Time",
            yaxis=dict(title="Fuel (m³)", showgrid=True, zeroline=True),
            yaxis2=dict(title="Steam (t)", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=470,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Timestamp column found; showing totals only.")

with tab2:
    st.subheader("Efficiency vs O₂%")
    if o2_col:
        fig = px.scatter(
            df, x=o2_col, y=eff_col, size="Total_Fuel_m3",
            color="Total_Steam_Tons", color_continuous_scale="Turbo",
            labels={o2_col: "O₂ %", eff_col: "Efficiency %"}, 
            hover_data=[ts_col],
            title="Efficiency vs Oxygen"
        )
        fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("O₂ column not found; skipping this chart.")

with tab3:
    st.subheader("Boiler Totals and Comparison")
    comp = pd.DataFrame({
        "Boiler": ["Boiler 1", "Boiler 2"],
        "Fuel_m3":  [df[b1_fuel].sum(),  df[b2_fuel].sum()],
        "Steam_t":  [df[b1_steam].sum(), df[b2_steam].sum()]
    })
    fig = px.bar(comp.melt(id_vars="Boiler"), x="Boiler", y="value", color='variable', barmode="group", text_auto=True,
                 title="Fuel & Steam Totals")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(comp)

with tab4:
    st.subheader("Data Heatmap")
    if ts_col:
        pivot = df[[ts_col, eff_col, o2_col]].copy().dropna()
        pivot.set_index(ts_col, inplace=True)
        st.dataframe(pivot.style.background_gradient(cmap='YlGnBu'))
    else:
        st.info("Timestamp not found for heatmap.")

with st.expander("📂 Download / Raw Data"):
    st.dataframe(df)
    st.download_button('Download CSV', df.to_csv(index=False), file_name='boiler_dashboard_filtered.csv', mime='text/csv')

st.caption("Made with Streamlit • Developed by Your Team 🚀")
