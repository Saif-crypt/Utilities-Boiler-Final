import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Boiler Plant Dashboard", layout="wide")
st.title("🔥 Boiler Plant Dashboard")
st.caption("Monitor performance, efficiency, and fuel usage of Boiler 1 & Boiler 2")

# ---- Load data ----
CSV_PATH = "boiler_phase3_dashboard.csv"  # change if your file is named differently
df = pd.read_csv(CSV_PATH)

# ---- Flexible column mapping ----
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

# ---- Prepare fields ----
if ts_col:
    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")

df["Total_Fuel_m3"]     = df[b1_fuel].fillna(0) + df[b2_fuel].fillna(0)
df["Total_Steam_Tons"]  = df[b1_steam].fillna(0) + df[b2_steam].fillna(0)

if eff_col is None:
    # Simple proxy if not provided
    df["Overall_Efficiency_%"] = (df["Total_Steam_Tons"] / df["Total_Fuel_m3"].replace(0, np.nan)) * 100
    eff_col = "Overall_Efficiency_%"

# ---- KPIs ----
c1, c2, c3 = st.columns(3)
c1.metric("Total Fuel (m³)", f"{df['Total_Fuel_m3'].sum():,.0f}")
c2.metric("Total Steam (tons)", f"{df['Total_Steam_Tons'].sum():,.0f}")
c3.metric("Avg Efficiency (%)", f"{df[eff_col].mean():.2f}")

# ---- Tabs ----
tab1, tab2, tab3 = st.tabs(["📊 Trends", "⚡ Efficiency vs O₂", "🛠 Boiler Comparison"])

with tab1:
    st.subheader("Fuel & Steam over Time")
    if ts_col:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[ts_col], y=df["Total_Fuel_m3"], name="Total Fuel (m³)"))
        fig.add_trace(go.Scatter(x=df[ts_col], y=df["Total_Steam_Tons"], name="Total Steam (t)", yaxis="y2"))
        fig.update_layout(
            xaxis_title="Time",
            yaxis=dict(title="Fuel (m³)"),
            yaxis2=dict(title="Steam (t)", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Timestamp column found; showing totals only.")

with tab2:
    st.subheader("Efficiency vs O₂%")
    if o2_col:
        fig = px.scatter(
            df, x=o2_col, y=eff_col, size="Total_Fuel_m3", color="Total_Steam_Tons",
            labels={o2_col: "O₂ %", eff_col: "Efficiency %"}, title="Efficiency vs Oxygen"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("O₂ column not found; skipping this chart.")

with tab3:
    st.subheader("Boiler Totals")
    comp = pd.DataFrame({
        "Boiler": ["Boiler 1", "Boiler 2"],
        "Fuel_m3":  [df[b1_fuel].sum(),  df[b2_fuel].sum()],
        "Steam_t":  [df[b1_steam].sum(), df[b2_steam].sum()]
    })
    fig = px.bar(comp, x="Boiler", y=["Fuel_m3", "Steam_t"], barmode="group", text_auto=True,
                 title="Fuel & Steam Totals")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("📂 Raw data"):
    st.dataframe(df)
