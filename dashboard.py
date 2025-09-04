import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------
# Load Data
# ---------------------------
df = pd.read_csv("boiler_phase3_dashboard.csv", parse_dates=["Timestamp"])

st.set_page_config(page_title="Boiler Plant Dashboard", layout="wide")

st.title("🔥 Boiler Plant Dashboard")
st.markdown("Monitor performance, efficiency, and fuel usage of Boiler 1 & Boiler 2")

# ---------------------------
# KPIs
# ---------------------------
total_fuel = df["Fuel_Consumption_m3"].sum()
total_steam = df["Steam_Flow_TPH"].sum()
avg_eff = df["Boiler_Efficiency"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Fuel Used (m³)", f"{total_fuel:,.0f}")
col2.metric("Total Steam Generated (TPH)", f"{total_steam:,.0f}")
col3.metric("Avg Efficiency (%)", f"{avg_eff:.2f}")

# ---------------------------
# Tabs for Analysis
# ---------------------------
tab1, tab2, tab3 = st.tabs(["📊 Trends", "⚡ Efficiency Analysis", "🛠 Boiler Comparison"])

with tab1:
    st.subheader("Fuel vs Steam Trend")
    fig1 = px.line(df, x="Timestamp", y=["Fuel_Consumption_m3", "Steam_Flow_TPH"],
                   labels={"value": "Reading", "variable": "Parameter"},
                   title="Fuel Consumption vs Steam Flow Over Time")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("Efficiency vs O₂%")
    fig2 = px.scatter(df, x="O2_Percent", y="Boiler_Efficiency",
                      size="Fuel_Consumption_m3", color="Steam_Flow_TPH",
                      hover_data=["Timestamp"],
                      title="Boiler Efficiency vs Oxygen %")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("ΔT Stack Temperature Distribution")
    fig3 = px.histogram(df, x="DeltaT_Stack", nbins=20, color_discrete_sequence=["red"])
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("Boiler 1 vs Boiler 2 Performance")
    avg_data = df.groupby("Boiler")[
        ["Fuel_Consumption_m3", "Steam_Flow_TPH", "Boiler_Efficiency"]
    ].mean().reset_index()

    fig4 = px.bar(avg_data, x="Boiler", y="Boiler_Efficiency",
                  color="Boiler", text_auto=".2f",
                  title="Average Efficiency by Boiler")
    st.plotly_chart(fig4, use_container_width=True)

# ---------------------------
# Raw Data Expander
# ---------------------------
with st.expander("📂 View Raw Data"):
    st.dataframe(df)
